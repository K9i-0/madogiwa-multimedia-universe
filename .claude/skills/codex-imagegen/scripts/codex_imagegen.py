#!/usr/bin/env python3
"""Generate or edit images from Claude Code via Codex's built-in image_gen tool.

Uses the ChatGPT subscription quota of the logged-in Codex CLI (no OPENAI_API_KEY).
Images are collected from $CODEX_HOME/generated_images/<thread_id>/ of this run only,
so concurrent Codex sessions are never mixed in.

Example:
  python3 codex_imagegen.py --out out/bg.png --prompt-file prompt.txt --ref sheet.png
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

INSTRUCTION = """You are an image generation backend called from another agent.
Use ONLY the built-in image_gen tool. Never run scripts/image_gen.py, never call an
OpenAI API with an API key, never fall back to another model, and never write SVG/HTML
substitutes. Do not create or copy files yourself; just call image_gen.
Attached images (if any) are, in order: {refs}.
Generate exactly {count} image(s). If the request cannot be generated, explain why briefly.

=== Image request ===
{prompt}
"""


def numbered(out: Path, idx: int, total: int) -> Path:
    if total == 1:
        return out
    return out.with_name(f"{out.stem}-{idx}{out.suffix}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt", help="image request text")
    src.add_argument("--prompt-file", type=Path, help="file containing the image request")
    ap.add_argument("--ref", type=Path, action="append", default=[],
                    help="reference / edit-target image (repeatable, order is kept)")
    ap.add_argument("--ref-label", action="append", default=[],
                    help="role of each --ref in the same order, e.g. 'edit target', 'character sheet'")
    ap.add_argument("--out", type=Path, required=True,
                    help="destination PNG; with --count>1, -1/-2... suffixes are added")
    ap.add_argument("--count", type=int, default=1, help="number of images (one prompt, variants)")
    ap.add_argument("--overwrite", action="store_true", help="allow overwriting existing outputs")
    ap.add_argument("--timeout", type=int, default=900, help="seconds")
    ap.add_argument("--model", help="optional Codex model override (codex -m)")
    args = ap.parse_args()

    prompt = args.prompt if args.prompt is not None else args.prompt_file.read_text(encoding="utf-8")
    refs = [p.expanduser().resolve() for p in args.ref]
    for p in refs:
        if not p.is_file():
            ap.error(f"reference not found: {p}")
    labels = args.ref_label + [""] * (len(refs) - len(args.ref_label))
    ref_desc = "; ".join(
        f"Image {i + 1}: {p.name}" + (f" ({labels[i]})" if labels[i] else "") for i, p in enumerate(refs)
    ) or "none"

    out = args.out.expanduser().resolve()
    targets = [numbered(out, i + 1, args.count) for i in range(args.count)]
    if not args.overwrite:
        exists = [str(t) for t in targets if t.exists()]
        if exists:
            ap.error("output exists (use a versioned name or --overwrite): " + ", ".join(exists))

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    full_prompt = INSTRUCTION.format(refs=ref_desc, count=args.count, prompt=prompt.strip())

    with tempfile.TemporaryDirectory(prefix="codex-imagegen-") as work:
        cmd = ["codex", "exec", "--json", "--skip-git-repo-check", "-s", "read-only", "-C", work,
               "-o", str(Path(work) / "last.txt")]
        if args.model:
            cmd += ["-m", args.model]
        # The prompt goes through stdin ("-") so the variadic -i never swallows it.
        cmd += ["-"]
        for p in refs:
            cmd += ["-i", str(p)]
        try:
            proc = subprocess.run(cmd, input=full_prompt, capture_output=True, text=True,
                                  timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(json.dumps({"ok": False, "error": f"timeout after {args.timeout}s"}))
            return 2

        thread_id = None
        for line in proc.stdout.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "thread.started":
                thread_id = ev.get("thread_id")
                break
        last = Path(work, "last.txt").read_text(encoding="utf-8").strip() if Path(work, "last.txt").exists() else ""

    gen_dir = codex_home / "generated_images" / thread_id if thread_id else None
    images = sorted(gen_dir.glob("*.png"), key=lambda p: p.stat().st_mtime) if gen_dir and gen_dir.is_dir() else []
    if not images:
        print(json.dumps({"ok": False, "error": "no image generated", "exit_code": proc.returncode,
                          "thread_id": thread_id, "codex_message": last,
                          "stderr_tail": proc.stderr[-2000:]}, ensure_ascii=False, indent=2))
        return 1

    if len(images) != len(targets):
        targets = [numbered(out, i + 1, len(images)) for i in range(len(images))]
        if not args.overwrite and any(t.exists() for t in targets):
            ap.error("output exists for the actual image count; rerun with another --out")
    out.parent.mkdir(parents=True, exist_ok=True)
    for srcp, dst in zip(images, targets):
        shutil.copy2(srcp, dst)
    print(json.dumps({"ok": True, "outputs": [str(t) for t in targets], "thread_id": thread_id,
                      "source_dir": str(gen_dir), "codex_message": last},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
