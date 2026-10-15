#!/usr/bin/env python3
"""Prepare retained production examples for the v3 human-facing tutorial.

Run with a Python that has Pillow, e.g. sets/02/.venv/bin/python. Source art is
never regenerated or retouched. Historical drafts used as production inputs are
copied once into input/tips; adopted sources already tracked in the mono repo
remain the originals. Crops remove only surrounding content. GIF/APNG playback
is composited by Pillow, then frame-selected by Remotion's composition clock.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUBLIC = HERE / "remotion/public"
OUT = PUBLIC / "tips"
SET1 = ROOT / "27_LINE_STICKERS/sets/01"
SET2 = ROOT / "27_LINE_STICKERS/sets/02"
records: list[dict] = []
images: dict = {}
animations: dict = {}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def public(path: Path) -> str:
    return path.relative_to(PUBLIC).as_posix()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def retained(source: Path, name: str) -> Path:
    """Adopt an ignored historical draft without a mutable hardlink."""
    dest = HERE / "input/tips" / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(source, dest)
    if source.exists() and sha(source) != sha(dest):
        raise ValueError(f"Historical input changed; review explicitly: {source}")
    records.append({"source": rel(source), "adoptedInput": rel(dest),
                    "sha256": sha(dest), "operation": "unchanged independent copy of retained production draft"})
    return dest


def still(key: str, source: Path, note: str, crop=None) -> None:
    dest = OUT / "images" / f"{key}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        im = opened.convert("RGBA")
        if crop is not None:
            im = im.crop(crop)
        im.save(dest, optimize=True)
    images[key] = {"path": public(dest), "width": im.width, "height": im.height,
                   "source": rel(source), "note": note}
    records.append({"key": key, "source": rel(source), "sourceSha256": sha(source),
                    "output": public(dest), "outputSha256": sha(dest), "crop": crop,
                    "operation": "lossless RGBA decode" + (" and exact rectangle crop" if crop else ""),
                    "note": note})


def animation(key: str, source: Path, note: str) -> None:
    dest = OUT / "animations" / key
    dest.mkdir(parents=True, exist_ok=True)
    frames = []
    cursor = 0.0
    with Image.open(source) as im:
        start = 1 if im.info.get("default_image", False) else 0
        original_loop = im.info.get("loop")
        assert im.is_animated
        width, height = im.size
        for i in range(start, im.n_frames):
            im.seek(i)
            rgba = im.convert("RGBA")
            output = dest / f"frame-{i-start:03}.png"
            rgba.save(output, optimize=True)
            assert Image.open(output).convert("RGBA").tobytes() == rgba.tobytes()
            duration = round(float(im.info["duration"]), 6)
            frames.append({"path": public(output), "durationMs": duration,
                           "startMs": cursor, "endMs": round(cursor + duration, 6)})
            cursor = round(cursor + duration, 6)
    animations[key] = {"id": key, "width": width, "height": height,
                       "durationMs": cursor, "frameCount": len(frames), "frames": frames,
                       "originalLoop": original_loop, "source": rel(source), "note": note}
    records.append({"key": key, "source": rel(source), "sourceSha256": sha(source),
                    "outputDirectory": public(dest), "durationMs": cursor, "frames": len(frames),
                    "operation": "Pillow full composited GIF/APNG frames; disposal and blend applied",
                    "note": note})


def main() -> None:
    for letter, filename in [("A", "A_action"), ("B", "B_deadpan"), ("C", "C_exaggerated")]:
        source = retained(SET2 / f"drafts/comparison/{filename}.png", f"ideas-{letter}.png")
        still(f"ideas{letter}", source, f"実際の第2弾8個入り初期案{letter}。文字と絵を含む元生成画像。")
    for letter in "ABC":
        source = retained(SET2 / f"drafts/work-check/{letter}.png", f"work-{letter}.png")
        still(f"work{letter}", source, {"A": "立ち姿の静止案。未採用。", "B": "パーティションに肘を置く静止案。採用。", "C": "普通の椅子で指差す静止案。後に椅子をアーロンチュア化して二流へ転用。"}[letter])
        draft = retained(SET2 / f"drafts/elbow-weight/{letter}/sticker.png", f"elbow-{letter}.png")
        animation(f"elbow{letter}", draft, "肘に体重をかける旧試作。A/B/Cの3案はすべて不採用。")

    raw = SET2 / "source/01_ohayo/reference.png"
    redrawn = SET2 / "source/01_ohayo/art-generated.png"
    still("redrawBefore", raw, "8個sheetの反復編集後から取り出した、実際の再描画参照。文字と隣セル断片のみ表示範囲外。", (24, 106, 368, 464))
    still("redrawAfter", redrawn, "同じ構図を1枚で描き直した実際の生成原画。線や口も完全な同一画素ではない。", (74, 29, 1183, 1223))
    still("redrawBeforeFace", raw, "再描画前の元画素拡大用。画像劣化を追加していない。", (120, 100, 240, 228))
    still("redrawAfterFace", redrawn, "再描画後の元画素拡大用。", (410, 20, 800, 436))
    still("canonicalSobaya", ROOT / "03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png", "現在のそば屋人物同一性の正典シート。")
    still("niryuAdopted", SET2 / "stickers/04_niryu/still.png", "椅子の静止候補からアーロンチュアへ修正し、二流に転用した完成スタンプ。")
    animation("workAdopted", SET2 / "stickers/02_hataraiteruka/sticker.png", "最終採用。肩・胸・頭が連動して小さく傾き、返事を待つ。")
    animation("niryuAdopted", SET2 / "stickers/04_niryu/sticker.png", "二流の最終採用。頭の回転なし、指差しのみ。")
    animation("nominiAdopted", SET2 / "stickers/07_nomini/sticker.png", "飲みに行こうの最終採用。正面から書類を捨て、背を向けて振り返る。")
    for bg in ["white", "black"]:
        animation(f"first{bg.title()}", SET1 / f"all-members-{bg}-preview.gif", "実際の第一弾8個の確認用GIF。白黒に新たな欠陥を追加していない。")
        still(f"first{bg.title()}", SET1 / f"all-members-{bg}-still.png", "実際の第一弾完成確認画像。")

    # These are actual historical white-matte input and actual corresponding
    # completed output. Never simulate a defective result by adding white dirt.
    still("matteCaptionBefore", SET1 / "source/sobaya/caption.png", "実際の白背景付き文字入力。失敗版を人工的に作ったものではない。")
    still("matteCaptionAfter", SET1 / "stickers/sobaya/still.png", "実際の完成スタンプから対応文字領域を切り出したもの。閉じ穴透過と意図的な白縁。白縁が入力文字高より2px下まで伸びるため90px。", (0, 0, 400, 90))
    still("matteBodyBefore", SET1 / "source/sobaya/poses/00.png", "実際の白背景付き原画。白い服・泡もあるため単純な白一括消去は不適切。")
    still("matteBodyAfter", SET1 / "stickers/sobaya/still.png", "同じ先頭ポーズの実際の透過済み完成画像。描き直しではなく切抜き・縮尺・配置処理。", (0, 92, 400, 400))
    # Additional retained source references for the sprite-sheet explanation.
    still("yotanSheet", SET1 / "source/yotan/keyframes.png", "第一弾の実際の3列2行原画。")
    for i in range(4):
        still(f"sobayaPose{i}", SET1 / f"source/sobaya/poses/{i:02}.png", "第一弾そば屋の実際の4採用原画。12原画sheetを再構成したものではない。")

    manifest = {"version": 3, "images": images, "animations": animations,
                "playback": {"timebase": "Remotion frame / fps", "select": "t=(frame/fps*1000)%durationMs; first frame with t < endMs", "repeatForReview": True},
                "historicalNotes": ["8個入り案・候補画像は第2弾。第一弾の完成品と工程例へ補足として使う。", "elbowA/B/Cは全不採用。workAdoptedだけが採用された動き。", "matteCaptionBeforeは元の白背景付き入力。故意に汚れを足した失敗版ではない。", "art-generated再描画は元構図に沿うが形や顔の微差がある。完全一致とは称さない。"]}
    write_json(OUT / "manifest.json", manifest)
    write_json(HERE / "remotion/src/tips-assets.json", manifest)
    write_json(HERE / "asset_sources_v3.json", {"generator": "prepare_tips_assets.py", "preparedOn": "2026-10-15", "records": records,
               "imageEdits": "No Imagegen calls, no artificial degradation or defects. Lossless decode/crop only.",
               "verifiedLegacyTools": [{"source": rel(SET1 / "tools/matte.py"), "sha256": sha(SET1 / "tools/matte.py"), "purpose": "OpenCV contours/masks, white-matte removal, enclosed white preservation, caption transparency"},
               {"source": rel(SET1 / "tools/build.mjs"), "sha256": sha(SET1 / "tools/build.mjs"), "purpose": "ImageMagick crop/resize/composite, floodfill, connected components, APNG/GIF assembly"}],
               "limitations": manifest["historicalNotes"]})
    print(json.dumps({"images": len(images), "animations": len(animations), "decodedFrames": sum(a["frameCount"] for a in animations.values()), "manifest": str(OUT / "manifest.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
