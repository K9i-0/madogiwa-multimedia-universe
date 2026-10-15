#!/usr/bin/env python3
"""Prepare real first-series sticker assets for deterministic Remotion playback.

Requires Pillow (python -m pip install Pillow). Existing adopted assets are never
re-matted or altered. Frames are decoded from the FINAL APNG, including its
disposal/blend semantics, and saved losslessly as RGBA PNG. For review playback,
the renderer intentionally repeats the recorded 3-second cycle; submitted APNGs
retain their original one-play flag.

Run from any directory. Pass --refresh-store to refresh the cached official
listing HTML; otherwise a cached download is reused. The adopted listing image
under input/ is always preferred and never replaced by a refreshed download.
Outputs are reproducible build inputs under remotion/public, and provenance is
recorded in asset_sources.json.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import urllib.request

from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SET = ROOT / "27_LINE_STICKERS/sets/01"
PUBLIC = HERE / "remotion/public"
CACHE = HERE / ".asset-cache"
STORE_URL = "https://store.line.me/stickershop/product/37292753/ja"
FETCH_DATE = "2026-10-15"
records: list[dict] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def public_path(path: Path) -> str:
    return path.relative_to(PUBLIC).as_posix()


def publish(source: Path, dest: Path, note: str = "") -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # A render may be reading this pathname. Keep identical existing assets in
    # place, even when their inode differs from the canonical input.
    source_sha = sha(source)
    if dest.exists() and not os.path.samefile(source, dest) and sha(dest) != source_sha:
        dest.unlink()
    if not dest.exists():
        try:
            os.link(source, dest)
        except OSError:
            shutil.copy2(source, dest)
    records.append({"source": relative(source), "publicPath": public_path(dest),
                    "sha256": source_sha, "operation": "hardlink/copy, unchanged", "note": note})
    return public_path(dest)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch(url: str, dest: Path, refresh: bool = False) -> Path:
    if not dest.exists() or refresh:
        dest.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 MMUProductionAssetAudit/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            dest.write_bytes(response.read())
    return dest


def decode(member: dict) -> dict:
    name = member["id"]
    src = SET / "stickers" / name / "sticker.png"
    dest = PUBLIC / "stickers" / name
    dest.mkdir(parents=True, exist_ok=True)
    frames = []
    cursor = 0
    with Image.open(src) as apng:
        assert apng.is_animated, f"{src} is not an animation"
        first_animation_frame = 1 if apng.info.get("default_image", False) else 0
        original_plays = apng.info.get("loop")
        for i in range(first_animation_frame, apng.n_frames):
            apng.seek(i)
            frame = apng.convert("RGBA")
            duration = round(float(apng.info["duration"]), 6)
            filename = dest / f"frame-{i-first_animation_frame:02d}.png"
            frame.save(filename, optimize=True)
            assert Image.open(filename).convert("RGBA").tobytes() == frame.tobytes()
            frames.append({"path": public_path(filename), "durationMs": duration,
                           "startMs": cursor, "endMs": round(cursor + duration, 6)})
            cursor = round(cursor + duration, 6)
        assert apng.size == (320, 270)
        assert abs(cursor - 3000) < 0.001
        result = {**member, "width": apng.width, "height": apng.height,
                  "durationMs": cursor, "frameCount": len(frames), "originalPlays": original_plays,
                  "source": relative(src), "frames": frames,
                  "still": publish(SET / "stickers" / name / "still.png", dest / "still.png",
                                   "Adopted 400px still; final APNG frames are 320x270.")}
    write_json(dest / "durations.json", {"durationMs": cursor, "frames": frames})
    records.append({"source": relative(src), "sha256": sha(src),
                    "publicDirectory": public_path(dest), "frames": len(frames),
                    "durationMs": cursor, "operation": "Pillow APNG composite decode; original RGBA pixels preserved",
                    "note": "Review may repeat this cycle; LINE file original play count is unchanged."})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-store", action="store_true")
    args = parser.parse_args()
    data = json.loads((SET / "set.json").read_text())
    members = {m["id"]: decode(m) for m in data["members"]}

    sources = {
        "sobayaPoses": [publish(SET / f"source/sobaya/poses/{i:02}.png",
                                  PUBLIC / f"stickers/source/sobaya/poses/{i:02}.png",
                                  "One of four adopted drawings, not a fabricated 12-cell source sheet.") for i in range(4)],
        "sobayaReference": publish(SET / "source/sobaya/reference.png", PUBLIC / "stickers/source/sobaya/reference.png"),
        "sobayaCaption": publish(SET / "source/sobaya/caption.png", PUBLIC / "stickers/source/sobaya/caption.png"),
        "sobayaCanonicalSheet": publish(ROOT / "03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png",
                                        PUBLIC / "stickers/source/sobaya/canonical-sheet.png",
                                        "Current canonical identity sheet, separate from first-series illustration style."),
        "yotanSheet": publish(SET / "source/yotan/keyframes.png", PUBLIC / "stickers/source/yotan/keyframes.png",
                              "Actual retained 3x2 generated pose sheet."),
        "yotanReference": publish(SET / "source/yotan/reference.png", PUBLIC / "stickers/source/yotan/reference.png"),
        "whiteOverview": publish(SET / "all-members-white-still.png", PUBLIC / "stickers/overview-white.png"),
        "blackOverview": publish(SET / "all-members-black-still.png", PUBLIC / "stickers/overview-black.png"),
    }
    sheet = Image.open(SET / "source/yotan/keyframes.png")
    cw, ch = sheet.width // 3, sheet.height // 2
    sources["yotanSheetCells"] = []
    for i in range(6):
        dest = PUBLIC / f"stickers/source/yotan/cell-{i:02}.png"
        sheet.crop(((i % 3) * cw, (i // 3) * ch, (i % 3 + 1) * cw, (i // 3 + 1) * ch)).save(dest)
        sources["yotanSheetCells"].append(public_path(dest))
    records.append({"source": relative(SET / "source/yotan/keyframes.png"),
                    "outputs": sources["yotanSheetCells"], "operation": "3x2 exact cell crop without rescale or retouch"})

    duo = ROOT / "03_SCRIPTS/00_TEMPLATES/characters/commentary_duo_v1"
    expressions = sorted((duo / "exports").glob("*.png"))
    assert len(expressions) == 32, "Expected 32 canonical commentary expression exports"
    for source in expressions:
        publish(source, PUBLIC / "expressions" / source.name, "Canonical adopted commentary expression export, unchanged.")
    publish(duo / "takosan_blink.png", PUBLIC / "takosan_blink.png", "Canonical shared blink, no redraw.")

    source_html = fetch(STORE_URL, CACHE / "line-store-37292753.html", args.refresh_store)
    page = source_html.read_text(encoding="utf-8")
    product = json.loads(re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', page, re.S).group(1))
    previews = [json.loads(html.unescape(x)) for x in re.findall(r"data-preview='([^']+)'", page)]
    listing = next(p for p in previews if p.get("id") == "37292753")
    main_url = product["image"]
    main_file = HERE / "input/line-store-main-37292753.png"
    if not main_file.exists():
        downloaded = fetch(main_url, CACHE / "store-main.png", args.refresh_store)
        main_file.parent.mkdir(parents=True, exist_ok=True)
        # Keep the production input independent from mutable download caches.
        shutil.copy2(downloaded, main_file)
    main_path = publish(main_file, PUBLIC / "stickers/store/main.png", "Adopted actual LINE STORE listing image, unchanged.")
    records[-1]["sourceUrl"] = main_url
    store = {"url": STORE_URL, "productId": "37292753", "checkedOn": FETCH_DATE,
             "title": product["name"], "description": product["description"],
             "seller": product["offers"]["seller"]["name"], "type": listing["type"],
             "priceYen": int(product["offers"]["price"]), "hasPurchaseButton": 'data-test="purchase-btn"' in page,
             "mainImage": main_path, "mainImageUrl": main_url,
             "animationUrl": listing["animationUrl"], "submissionHandledBy": "そば屋さん（ユーザー共有）",
             "presentationNote": "実物の掲載画像と掲載情報。画面キャプチャではない。価格は確認日の参考情報。",
             "localListingAssetsNote": "申請に使用した動く版main/tabはローカル未収録。販売中であることとは別。"}
    write_json(PUBLIC / "stickers/store/metadata.json", store)
    records.append({"sourceUrl": STORE_URL, "fetchedOn": FETCH_DATE, "cachedHtml": relative(source_html),
                    "sha256": sha(source_html), "operation": "Read official Product structured data and preview attributes",
                    "evidence": {"type": listing["type"], "purchaseButton": store["hasPurchaseButton"]}})
    records.append({"source": relative(main_file), "sourceUrl": main_url,
                    "publicPath": main_path, "sha256": sha(main_file),
                    "operation": "Adopted production input from original download, unchanged"})

    manifest = {"version": 1, "sourceSet": "27_LINE_STICKERS/sets/01", "order": list(members),
                "members": members, "sources": sources, "store": store,
                "playback": {"timebase": "composition frame / fps, never Date.now or browser animated Img",
                             "select": "t=(frame/fps*1000)%durationMs; first frame with t < endMs",
                             "reviewLoops": True, "sourceAPNGPlays": 1},
                "sobayaAssembly": {"adoptedPoseCount": 4, "deliveryFrameCount": 13,
                                   "poseOrder": [0,1,2,3,2,1,0,1,2,3,2,1,0],
                                   "durationsMs": [90]*12+[1920],
                                   "note": "Original prompt requested 12 cells; retained source is four adopted drawings."}}
    write_json(PUBLIC / "stickers/manifest.json", manifest)
    write_json(HERE / "asset_sources.json", {"preparedOn": FETCH_DATE, "generator": "prepare_assets.py",
               "set": "27_LINE_STICKERS/sets/01", "sources": records,
               "store": store, "limitations": ["No retained raw Sobaya 12-pose sheet; do not depict reconstructed sheet as historical input.",
               "Use global composition frame for all sticker previews; no browser GIF/APNG timebase.",
               "First series is on sale; submitted animated main/tab files are not archived locally."]})
    print(json.dumps({"members": len(members), "decodedFrames": sum(m["frameCount"] for m in members.values()),
                      "manifest": str(PUBLIC / "stickers/manifest.json"), "storeTitle": store["title"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
