#!/usr/bin/env python3
"""Prepare v5's genuine failed exports, report screenshot and second-set grid.

No art is regenerated or damaged. Historical APNG bytes come from Git; the report
screenshot is an unchanged retained user attachment. PNGs are decoded frames or
exact crops only. Run after prepare_tips_assets.py (also called by that script).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUBLIC = HERE / "remotion/public"
OUT = PUBLIC / "tips/history"
INPUT = HERE / "input/alpha-history"
BEFORE = "1bcd3478d9fba7f0b319a3b9a976e9ed1fcd17a2"
AFTER = "4151d63c5137a1b111b82f4ed53a3cc67467b9f4"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    manifest_path = HERE / "remotion/src/tips-assets.json"
    manifest = json.loads(manifest_path.read_text())
    records = []
    INPUT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    def still(key: str, source: Path, note: str, crop=None) -> None:
        dest = OUT / f"{key}.png"
        with Image.open(source) as im:
            im.seek(0)
            rgba = im.convert("RGBA")
            if crop is not None:
                rgba = rgba.crop(crop)
            rgba.save(dest, optimize=True)
        manifest["images"][key] = {
            "path": dest.relative_to(PUBLIC).as_posix(), "width": rgba.width,
            "height": rgba.height, "source": source.relative_to(ROOT).as_posix(), "note": note,
        }
        records.append({"key": key, "source": source.relative_to(ROOT).as_posix(),
                        "sourceSha256": sha(source), "output": dest.relative_to(PUBLIC).as_posix(),
                        "outputSha256": sha(dest), "frame": 0, "crop": crop,
                        "operation": "lossless RGBA decode" + (" and exact crop" if crop else ""), "note": note})

    for stage, commit in [("Before", BEFORE), ("After", AFTER)]:
        for member in ["sobaya", "yametaro"]:
            git_path = f"27_LINE_STICKERS/sets/01/stickers/{member}/sticker.png"
            data = subprocess.check_output(["git", "show", f"{commit}:{git_path}"], cwd=ROOT)
            source = INPUT / f"{member}-{stage.lower()}.png"
            if source.exists() and source.read_bytes() != data:
                raise ValueError(f"Historical source changed: {source}")
            source.write_bytes(data)
            records.append({"adoptedInput": source.relative_to(ROOT).as_posix(), "commit": commit,
                            "gitPath": git_path, "sha256": sha(source), "operation": "byte-exact git blob extraction"})
            still(f"history{member.title()}{stage}", source, f"第一弾の実際の書き出し済みAPNG・先頭フレーム。{stage}。")
            if member == "sobaya":
                still(f"historyHair{stage}", source, "人物輪郭の白混入の比較。髪・顔周辺の同一範囲。", (132, 61, 250, 161))
                still(f"historyShirt{stage}", source, "右下の白Tシャツが欠けた箇所の同一範囲。", (175, 190, 282, 266))
                still(f"historyCaption{stage}", source, "完成出力の文字を比較。修正後の均一な細い白フチは可読性のため意図的に追加。", (45, 5, 277, 66))
            else:
                still(f"historyLetter{stage}", source, "ごめんやでの『め』内部に不透明の白が残る実例。同一範囲。", (90, 15, 165, 80))

    report = INPUT / "original_user_report_20261014.png"
    expected = "095bf2d59b46e23ecce15d030571d4994fc4e4edafc9fd62929bcb26a408608e"
    if not report.exists():
        shutil.copy2(HERE / "remotion/out/alpha-history-research/sessions/original_user_report_20261014.png", report)
    if sha(report) != expected:
        raise ValueError("Historical screenshot differs from original attachment")
    records.append({"adoptedInput": report.relative_to(ROOT).as_posix(), "sha256": sha(report),
                    "origin": "2026-10-14 16:00:30 JST user-reported registration screenshot",
                    "operation": "unchanged copy of recovered original attachment"})
    still("historyReport", report, "2026年10月14日、実際の登録後に届いた当時の不具合報告画像。無加工。")

    second_set = []
    for folder in sorted((ROOT / "27_LINE_STICKERS/sets/02/stickers").iterdir()):
        source = folder / "sticker.png"
        if not source.exists():
            continue
        key = f"second_{folder.name}"
        dest = PUBLIC / "tips/animations" / key
        dest.mkdir(parents=True, exist_ok=True)
        frames = []
        cursor = 0.0
        with Image.open(source) as im:
            width, height = im.size
            loop = im.info.get("loop")
            first = 1 if im.info.get("default_image", False) else 0
            for i in range(first, im.n_frames):
                im.seek(i)
                output = dest / f"frame-{i-first:03}.png"
                im.convert("RGBA").save(output, optimize=True)
                duration = round(float(im.info["duration"]), 6)
                frames.append({"path": output.relative_to(PUBLIC).as_posix(), "durationMs": duration,
                               "startMs": cursor, "endMs": round(cursor + duration, 6)})
                cursor = round(cursor + duration, 6)
        manifest["animations"][key] = {"id": key, "width": width, "height": height,
            "durationMs": cursor, "frameCount": len(frames), "frames": frames,
            "originalLoop": loop, "source": source.relative_to(ROOT).as_posix(), "note": "第二弾の最終採用APNG。"}
        second_set.append(key)
        records.append({"key": key, "source": source.relative_to(ROOT).as_posix(), "sourceSha256": sha(source),
                        "outputDirectory": dest.relative_to(PUBLIC).as_posix(), "frames": len(frames),
                        "operation": "Pillow full composited APNG frames; original durations retained"})
    assert len(second_set) == 8, second_set
    manifest["secondSet"] = second_set
    manifest["version"] = 5
    manifest["historicalNotes"] = [
        "第一弾と第二弾の両方を制作した時点の知見を紹介。8個入り案と候補比較は第二弾。",
        "elbowA/B/Cは全不採用。workAdoptedが採用された動き。",
        "v5の透過失敗例はGitから復元した当時の納品APNG。白背景入力や人工的な不良画像ではない。",
        "当時の不具合報告スクリーンショットも無加工で保存。",
        "白い服・仮面・泡、可読性のための細い均一な文字白フチは残す。輪郭の背景混入と区別。",
        "art-generated再描画は元構図に沿うが形や顔の微差がある。完全一致とは称さない。",
    ]
    write_json(manifest_path, manifest)
    write_json(PUBLIC / "tips/manifest.json", manifest)
    write_json(HERE / "asset_sources_v5.json", {"generator": "prepare_history_assets.py",
        "preparedOn": "2026-10-16", "records": records,
        "imageEdits": "No Imagegen calls, no artificial defects. Exact Git extraction, unchanged retained attachment, lossless decode and crop only.",
        "sourceResearch": "first_set_alpha_history.json", "limitations": manifest["historicalNotes"]})
    print(json.dumps({"historyImages": len([k for k in manifest["images"] if k.startswith("history")]),
                      "secondSet": len(second_set), "sourceRecords": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
