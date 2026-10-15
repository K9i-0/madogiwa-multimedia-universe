#!/usr/bin/env python3
"""Generate isolated VOICEVOX audition lines; never edit adopted voices or timelines.

All candidates use the same audition settings. These are this production's
comparison controls, not a claimed universal setting for なんJ videos.
"""
from __future__ import annotations

import argparse
import array
import copy
import datetime as dt
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import urllib.parse
import urllib.request
import wave

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
CANDIDATES = {
    "aoyama": ("青山龍星", "ノーマル"),
    "kurono": ("玄野武宏", "ノーマル"),
    "shirakami": ("白上虎太郎", "ふつう"),
}
SETTINGS = {
    "speedScale": 1.15,
    "pitchScale": 0,
    "intonationScale": 1.0,
    "volumeScale": 1,
    "prePhonemeLength": 0.10,
    "postPhonemeLength": 0.20,
    "outputSamplingRate": 48000,
    "outputStereo": False,
}
# Avoid splitting proper names into two unrelated accent phrases. These are
# audition choices, not a change to the canonical name pronunciation or voice.
KANA_REPLACEMENTS = {
    "intro-04": ("ヨオ'/タ'ンカラヤ", "ヨオ'タンカラヤ"),
    "main-01": ("ヤメ'/タ'ロオデ_ス", "ヤメタ'ロオデ_ス"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).encode()


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def request(base: str, path: str, *, params=None, body=None, post=False):
    url = base.rstrip("/") + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    raw = None if not post else (b"" if body is None else json_bytes(body))
    req = urllib.request.Request(
        url, data=raw, method="POST" if post else "GET",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        data = response.read()
    return data if path == "/synthesis" else json.loads(data)


def metrics(raw: bytes) -> dict:
    with wave.open(io.BytesIO(raw), "rb") as reader:
        assert reader.getsampwidth() == 2 and reader.getnchannels() == 1
        rate, frames = reader.getframerate(), reader.getnframes()
        pcm = array.array("h", reader.readframes(frames))
    if sys.byteorder != "little":
        pcm.byteswap()
    peak = max(map(abs, pcm), default=0) / 32768
    rms = math.sqrt(sum(x * x for x in pcm) / max(1, len(pcm))) / 32768
    active = [i for i, value in enumerate(pcm) if abs(value) >= 104]
    return {
        "sampleRate": rate, "sampleCount": frames, "channels": 1,
        "durationSeconds": frames / rate,
        "durationInFrames": math.ceil(frames / rate * 30),
        "metrics": {
            "peak": peak, "peakDbFS": 20 * math.log10(peak) if peak else None,
            "rmsDbFS": 20 * math.log10(rms) if rms else None,
            "clippedSamples": sum(abs(value) >= 32767 for value in pcm),
            "firstAboveMinus50DbSeconds": active[0] / rate if active else None,
            "lastAboveMinus50DbSeconds": active[-1] / rate if active else None,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", choices=CANDIDATES)
    parser.add_argument("--base-url", default="http://127.0.0.1:50021")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    source_path = HERE / "dialogue.json"
    record_path = EPISODE / "voice_record.json"
    dialogue = json.loads(source_path.read_text())[:16]
    recorded = {row["id"]: row for row in json.loads(record_path.read_text())["lines"]}
    selected = [row for row in dialogue if row["who"] == "yametaro"]
    assert len(selected) == 10 and dialogue[-1]["id"] == "main-03"
    speakers = request(args.base_url, "/speakers")
    engine = request(args.base_url, "/version")
    for candidate in args.candidate or CANDIDATES:
        name, style = CANDIDATES[candidate]
        speaker = next(s for s in speakers if s["name"] == name)
        speaker_id = next(s["id"] for s in speaker["styles"] if s["name"] == style)
        folder = HERE / "out" / "voice-candidates" / candidate
        folder.mkdir(parents=True, exist_ok=True)
        index = {
            "version": 1, "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
            "candidate": candidate, "label": f"VOICEVOX:{name}（{style}）",
            "engineVersion": engine, "speakerName": name,
            "speakerId": speaker_id, "speakerUuid": speaker["speaker_uuid"],
            "speakerVersion": speaker["version"], "style": style,
            "settings": SETTINGS, "subjectiveListening": False,
            "comparisonSettingNote": "今回の比較用設定。なんJ動画共通の設定を主張しない。",
            "credit": f"VOICEVOX:{name}",
            "sourceDialogueSha256": sha(source_path.read_bytes()),
            "sourceVoiceRecordSha256": sha(record_path.read_bytes()),
            "normalization": "none; preserve synthesized PCM for downstream mix",
            "postProcessing": "none; no tail trim or time stretch",
            "lines": [],
        }
        for row in selected:
            spoken = recorded[row["id"]]["spoken"]
            original_query = request(args.base_url, "/audio_query", post=True,
                                     params={"text": spoken, "speaker": speaker_id})
            query = copy.deepcopy(original_query)
            change = None
            if row["id"] in KANA_REPLACEMENTS:
                before, after = KANA_REPLACEMENTS[row["id"]]
                assert before in original_query["kana"], original_query["kana"]
                fixed_kana = original_query["kana"].replace(before, after)
                query["accent_phrases"] = request(
                    args.base_url, "/accent_phrases", post=True,
                    params={"text": fixed_kana, "speaker": speaker_id,
                            "is_kana": "true"},
                )
                query["kana"] = fixed_kana
                old_moras = [m["text"] for p in original_query["accent_phrases"] for m in p["moras"]]
                new_moras = [m["text"] for p in query["accent_phrases"] for m in p["moras"]]
                assert old_moras == new_moras, (old_moras, new_moras)
                change = {
                    "originalKana": original_query["kana"], "synthesisKana": fixed_kana,
                    "reason": "Keep the proper name in one accent phrase; audition accent choice.",
                    "subjectiveListening": False,
                }
            query.update(SETTINGS)
            request_identity = {
                "engineVersion": engine, "speakerVersion": speaker["version"],
                "speakerId": speaker_id, "query": query,
                "enableInterrogativeUpspeak": True,
            }
            query_hash = sha(json_bytes(request_identity))
            audio_path = folder / f'{row["id"]}_{query_hash[:12]}.wav'
            query_path = folder / f'{row["id"]}_{query_hash[:12]}.query.json'
            save_json(query_path, request_identity)
            if args.force or not audio_path.exists():
                raw = request(args.base_url, "/synthesis", post=True, body=query,
                              params={"speaker": speaker_id,
                                      "enable_interrogative_upspeak": "true"})
                audio_path.write_bytes(raw)
            raw = audio_path.read_bytes()
            stats = metrics(raw)
            assert stats["sampleRate"] == 48000 and stats["metrics"]["clippedSamples"] == 0
            entry = {
                "id": row["id"], "who": row["who"], "text": row["text"],
                "spoken": spoken, "kana": query["kana"],
                "audio": str(audio_path), "audioSha256": sha(raw),
                "query": query, "querySha256": query_hash,
                "queryFile": str(query_path), "originalQuery": original_query,
                "readingAdjustment": change, **stats,
            }
            index["lines"].append(entry)
            print(candidate, row["id"], f'{stats["durationSeconds"]:.3f}s', flush=True)
        index["totalVoiceSeconds"] = sum(row["durationSeconds"] for row in index["lines"])
        index["allClippedSamples"] = sum(row["metrics"]["clippedSamples"] for row in index["lines"])
        save_json(folder / "index.json", index)
        print(f"Wrote {folder / 'index.json'}", flush=True)


if __name__ == "__main__":
    main()
