"""作画回 編集v2（Wan v1生成動画のみを素材にした編集。追加生成・合成音なし）

処理:
- 720p Lanczos拡大（ffmpegでデコード時に一度だけ）
- 作画のコマ打ち: 対峙/余韻は3コマ、アクションは2コマ
- ヒットストップ: 命中フレームで静止→時間軸は元に戻る（音声と同期を保つ）
- インパクトフラッシュ: 白1コマ、反転/2値化コマの点滅
- 集中線（溜め）・流線（突進/吹き飛び）を手描き風に2コマごと描き替え
- 衝撃時のズーム＋減衰する揺れ、色ずれ
- ブルーム、ビネット
- ラストにサブタイトル
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC = HERE / "wan3_sakuga_v1_seed110101_480p.mp4"
OUT = HERE / (sys.argv[1] if len(sys.argv) > 1 else "final_sakuga_edit_v2_720p.mp4")
W, H, FPS = 1280, 720, 30
FONT = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/36a81f2dad2ef266c50802d85839e0201fcf4e57.asset/AssetData/ToppanBunkyuMidashiMinchoStdN-ExtraBold.otf"

# ---- タイミング（元動画のフレーム番号、30fps） ----
HITSTOPS = {238: 6, 333: 4, 728: 8}          # 命中フレーム: 静止コマ数
WHITE = {272, 333, 757}                      # 白フラッシュ1コマ
INVERT_FLICKER = [(268, 272), (728, 736)]    # 反転/通常を2コマごとに点滅
SHAKES = [(97, 0.5), (150, 0.35), (238, 0.5), (272, 0.8), (333, 0.7), (440, 0.4),
          (600, 0.35), (728, 1.0), (757, 1.0)]  # (開始フレーム, 強さ)
RADIAL = [(90, 97), (180, 238), (660, 728)]  # 集中線
STREAKS = [(97, 135, 1.0), (300, 333, -1.0)]  # 流線（向き）
TITLE_START = 815


def step_of(i):
    if i < 90 or i >= 790:
        return 3
    return 2


def build_source_map(n):
    m = []
    for i in range(n):
        s = i - (i % step_of(i))
        for hf, hl in HITSTOPS.items():
            if hf <= i < hf + hl:
                s = hf
        m.append(min(s, n - 1))
    return m


def shake_env(i):
    e = 0.0
    for f, a in SHAKES:
        if f <= i < f + 18:
            e = max(e, a * np.exp(-(i - f) / 5.0))
    return e


rng = np.random.default_rng(110101)


def radial_lines(i, strength=1.0):
    seed = i // 2
    r = np.random.default_rng(seed)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2 + r.uniform(-20, 20), H / 2 + r.uniform(-15, 15)
    R = 900
    for _ in range(110):
        a = r.uniform(0, 2 * np.pi)
        da = r.uniform(0.004, 0.018)
        inner = r.uniform(0.42, 0.62) * R
        pts = [
            (cx + np.cos(a - da) * R, cy + np.sin(a - da) * R),
            (cx + np.cos(a + da) * R, cy + np.sin(a + da) * R),
            (cx + np.cos(a) * inner, cy + np.sin(a) * inner * 0.62),
        ]
        d.polygon(pts, fill=int(255 * strength))
    return np.asarray(img, dtype=np.float32) / 255.0


def streak_lines(i, direction):
    r = np.random.default_rng(10_000 + i // 2)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    for _ in range(45):
        y = r.uniform(0, H)
        if H * 0.3 < y < H * 0.7 and r.random() < 0.7:
            continue  # 中心付近は空けて被写体を見せる
        length = r.uniform(200, 700)
        x0 = r.uniform(-200, W)
        th = r.uniform(1.5, 5)
        d.polygon([(x0, y - th), (x0 + length, y), (x0, y + th)], fill=230)
    a = np.asarray(img, dtype=np.float32) / 255.0
    return a[:, ::-1] if direction < 0 else a


def bloom(f):
    hi = np.clip(f - 0.6, 0, 1) * 2.0
    b = cv2.GaussianBlur(hi, (0, 0), 14)
    return 1 - (1 - f) * (1 - 0.45 * b)


yy, xx = np.mgrid[0:H, 0:W]
VIG = 1 - 0.28 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4
VIG = np.clip(VIG, 0.55, 1)[..., None].astype(np.float32)


def title_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 96)
    small = ImageFont.truetype(FONT, 34)
    t1, t2 = "赤坂決戦", "そば屋 対 たこさん"
    w1 = d.textlength(t1, font=big)
    w2 = d.textlength(t2, font=small)
    x1, y1 = W - w1 - 70, 80
    d.text((x1, y1), t1, font=big, fill=(255, 255, 255, 255), stroke_width=6, stroke_fill=(10, 10, 14, 255))
    d.text((W - w2 - 74, y1 + 118), t2, font=small, fill=(235, 60, 60, 255), stroke_width=4, stroke_fill=(10, 10, 14, 255))
    return np.asarray(img, dtype=np.float32) / 255.0


TITLE = title_layer()


def process(i, f):
    f = f.astype(np.float32) / 255.0
    # 線
    for a, b in RADIAL:
        if a <= i < b:
            m = radial_lines(i, 0.85)[..., None]
            f = f * (1 - m) + m * 0.97
    for a, b, d in STREAKS:
        if a <= i < b:
            m = streak_lines(i, d)[..., None] * 0.8
            f = f * (1 - m) + m * 0.97
    f = bloom(f)
    # 反転点滅（黒閃風）
    for a, b in INVERT_FLICKER:
        if a <= i < b and ((i - a) // 2) % 2 == 0:
            g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
            bw = (g < 0.45).astype(np.float32)  # 暗部を白、明部を黒へ
            red = np.clip((f[..., 0] - f[..., 1]) * 3, 0, 1)
            f = np.stack([np.maximum(bw, red), bw * (1 - red), bw * (1 - red)], -1)
    if i in WHITE:
        f = np.clip(f * 0.25 + 0.85, 0, 1)
    # 揺れ・ズーム・色ずれ
    e = shake_env(i)
    if e > 0.01:
        z = 1 + 0.07 * e
        dx = 26 * e * np.sin(i * 2.7)
        dy = 16 * e * np.cos(i * 3.3)
        M = np.float32([[z, 0, (1 - z) * W / 2 + dx], [0, z, (1 - z) * H / 2 + dy]])
        f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        s = int(round(7 * e))
        if s:
            f[..., 0] = np.roll(f[..., 0], -s, axis=1)
            f[..., 2] = np.roll(f[..., 2], s, axis=1)
    f = f * VIG
    # サブタイトル
    if i >= TITLE_START:
        alpha = min(1.0, (i - TITLE_START) / 8.0)
        a = TITLE[..., 3:4] * alpha
        f = f * (1 - a) + TITLE[..., :3] * a
    return (np.clip(f, 0, 1) * 255).astype(np.uint8)


def main():
    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(SRC), "-vf", f"scale={W}:{H}:flags=lanczos",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    frames = []
    sz = W * H * 3
    while True:
        buf = dec.stdout.read(sz)
        if len(buf) < sz:
            break
        frames.append(np.frombuffer(buf, np.uint8).reshape(H, W, 3))
    dec.wait()
    n = len(frames)
    smap = build_source_map(n)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", str(SRC), "-map", "0:v", "-map", "1:a",
         "-af", "equalizer=f=70:t=q:w=1:g=5,acompressor=threshold=-14dB:ratio=3:attack=5:release=120,alimiter=limit=0.95",
         "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(OUT)], stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(process(i, frames[smap[i]]).tobytes())
    enc.stdin.close()
    enc.wait()
    print(OUT, n, "frames")


if __name__ == "__main__":
    main()
