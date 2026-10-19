#!/usr/bin/env python3
"""Prepare VOICEVOX speech text without changing subtitles or engine user_dict."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


DEFAULT_DICTIONARY = Path(__file__).resolve().parents[1] / "references/readings.json"
ASCII_WORD = r"[A-Za-z0-9_]"
KANJI = r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff々]"


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def load_dictionary(path=DEFAULT_DICTIONARY, local_path=None):
    """Load shared rules and optional local overrides; paths are cwd independent."""
    documents = [_read_json(path)]
    if local_path is not None:
        documents.append(_read_json(local_path))
    scopes = {"common": "Always active"}
    merged = {"replacements": {}, "context_checks": {}}
    id_groups = {}
    for priority, document in enumerate(documents):
        if not isinstance(document, dict) or document.get("schema_version") != 1:
            raise ValueError("Dictionary must have schema_version: 1")
        declared = document.get("scopes", {})
        if not isinstance(declared, dict) or not all(
            _nonempty(k) and _nonempty(v) for k, v in declared.items()
        ):
            raise ValueError("scopes must map nonempty names to descriptions")
        scopes.update(declared)
        seen_ids, seen_surfaces = set(), set()
        for group in merged:
            entries = document.get(group, [])
            if not isinstance(entries, list):
                raise ValueError(f"{group} must be an array")
            for raw in entries:
                if not isinstance(raw, dict):
                    raise ValueError(f"{group} entries must be objects")
                entry = {**raw, "scope": raw.get("scope", "common"),
                         "match": raw.get("match", "literal"), "_priority": priority}
                for key in ("id", "surface", "source", "note"):
                    if not _nonempty(entry.get(key)):
                        raise ValueError(f"{group} entry requires nonempty {key}")
                entry_id = entry["id"]
                if entry_id in seen_ids:
                    raise ValueError(f"Duplicate id: {entry_id}")
                seen_ids.add(entry_id)
                if entry_id in id_groups and id_groups[entry_id] != group:
                    raise ValueError(f"Override cannot change rule type: {entry_id}")
                if entry["scope"] not in scopes:
                    raise ValueError(f"Unknown scope for {entry_id}: {entry['scope']}")
                if entry["match"] not in ("literal", "ascii_token", "kanji_word"):
                    raise ValueError(f"Unknown match mode for {entry_id}")
                surface_key = (group, entry["scope"], entry["surface"], entry["match"])
                if surface_key in seen_surfaces:
                    raise ValueError(f"Duplicate surface in scope: {entry['surface']}")
                seen_surfaces.add(surface_key)
                if group == "replacements":
                    if not _nonempty(entry.get("reading")):
                        raise ValueError(f"{entry_id} requires nonempty reading")
                else:
                    readings = entry.get("readings")
                    if not isinstance(readings, list) or not readings or not all(
                        _nonempty(value) for value in readings
                    ):
                        raise ValueError(f"{entry_id} requires readings array")
                id_groups[entry_id] = group
                merged[group][entry_id] = entry
    fingerprint = hashlib.sha256(json.dumps(
        documents, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    return {**{group: list(entries.values()) for group, entries in merged.items()},
            "scopes": scopes, "sha256": fingerprint}


def _active_rules(dictionary, scopes):
    selected = {"common", *scopes}
    unknown = selected - dictionary["scopes"].keys()
    if unknown:
        raise ValueError(f"Unknown scope(s): {', '.join(sorted(unknown))}")
    active = {group: [r for r in dictionary[group] if r["scope"] in selected]
              for group in ("replacements", "context_checks")}
    seen = {}
    for rule in active["replacements"]:
        key = (rule["surface"], rule["match"], rule["_priority"])
        if key in seen and seen[key] != rule["reading"]:
            raise ValueError(f"Conflicting readings in active scopes: {rule['surface']}")
        seen[key] = rule["reading"]
    return active, sorted(selected)


def _matches(text, rule):
    pattern = re.escape(rule["surface"])
    if rule["match"] == "ascii_token":
        if re.fullmatch(ASCII_WORD, rule["surface"][0]):
            pattern = rf"(?<!{ASCII_WORD})" + pattern
        if re.fullmatch(ASCII_WORD, rule["surface"][-1]):
            pattern += rf"(?!{ASCII_WORD})"
    elif rule["match"] == "kanji_word":
        pattern = rf"(?<!{KANJI})" + pattern + rf"(?!{KANJI})"
    return re.finditer(pattern, text)


def prepare_row(row, dictionary, scopes=()):
    """Return a new row, preserving text/metadata and adding speech + audit report."""
    if not isinstance(row, dict) or not _nonempty(row.get("text")):
        raise ValueError("Each input row requires nonempty text")
    active, selected = _active_rules(dictionary, scopes)
    report = {"method": "dictionary", "scopes": selected,
              "dictionary_sha256": dictionary["sha256"], "applied": [], "review": []}
    if "speech_override" in row:
        if not _nonempty(row["speech_override"]):
            raise ValueError("speech_override must be a nonempty string when provided")
        report["method"] = "explicit"
        return {**row, "speech": row["speech_override"], "reading_report": report}

    text = row["text"]
    matches = [(m.start(), m.end(), rule)
               for rule in active["replacements"] for m in _matches(text, rule)]
    matches.sort(key=lambda m: (m[0], -m[2]["_priority"], -(m[1] - m[0]), m[2]["id"]))
    parts, spans, cursor = [], [], 0
    for start, end, rule in matches:
        if start < cursor:
            continue
        parts.extend((text[cursor:start], rule["reading"]))
        spans.append((start, end))
        report["applied"].append({
            "id": rule["id"], "surface": text[start:end], "reading": rule["reading"],
            "scope": rule["scope"], "start": start, "end": end,
        })
        cursor = end
    parts.append(text[cursor:])
    for rule in active["context_checks"]:
        for match in _matches(text, rule):
            start, end = match.span()
            if any(a <= start and end <= b for a, b in spans):
                continue
            report["review"].append({
                "id": rule["id"], "surface": text[start:end], "start": start, "end": end,
                "readings": rule["readings"], "note": rule["note"],
            })
    report["review"].sort(key=lambda item: (item["start"], item["id"]))
    return {**row, "speech": "".join(parts), "reading_report": report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSON array of VOICEVOX rows")
    parser.add_argument("--output", type=Path, required=True, help="Separate prepared JSON file")
    parser.add_argument("--dictionary", type=Path, default=DEFAULT_DICTIONARY)
    parser.add_argument("--local-dictionary", type=Path)
    parser.add_argument("--scope", action="append", default=[], help="Opt-in scope; repeatable")
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must differ; preserve the subtitle source")
        dictionary = load_dictionary(args.dictionary, args.local_dictionary)
        _active_rules(dictionary, args.scope)
        rows = _read_json(args.input)
        if not isinstance(rows, list):
            raise ValueError("Input must be a JSON array")
        prepared = [prepare_row(row, dictionary, args.scope) for row in rows]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(prepared, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"Reading preparation failed: {exc}\n")
    applied = sum(len(row["reading_report"]["applied"]) for row in prepared)
    review = sum(len(row["reading_report"]["review"]) for row in prepared)
    print(f"Prepared {len(prepared)} rows; {applied} replacements; {review} context checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
