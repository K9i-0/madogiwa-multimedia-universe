"""作画回 編集v3：リタイミング（緩急）版

v2の仕上げ（線・フラッシュ・揺れ・ブルーム・タイトル）を継承し、
区間ごとに速度を変える。高速戦闘は早回し＋2コマ打ち、決めどころはスロー＋
オプティカルフロー補間で滑らかに（コマ打ちとの対比）。
音声は区間ごとに同じ速度で伸縮：スローは asetrate で低く重く、早回しは atempo（音程維持）。
素材はWan v1生成動画のみ。合成音なし。
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edit_v2 as v2  # noqa: E402

HERE = v2.HERE
SRC = v2.SRC
OUT = HERE / (sys.argv[1] if len(sys.argv) > 1 else "final_sakuga_edit_v3_retime_720p.mp4")
W, H, FPS, SR = v2.W, v2.H, 30, 44100

# (元の開始秒, 元の終了秒, 速度, 見せ方)  step: 1=補間スロー, 2=2コマ, 3=3コマ
SEGMENTS = [
    (0.00, 3.00, 1.5, 3),    # 対峙：詰める
    (3.00, 3.24, 0.4, 1),    # 仮面アップ：溜め
    (3.24, 4.30, 1.0, 2),    # 突進の踏み込み
    (4.30, 6.00, 1.8, 2),    # 触手連撃をさばく：高速
    (6.00, 7.70, 1.0, 2),    # 拳の溜め
    (7.70, 8.60, 0.3, 1),    # 拳が触れる瞬間：超スロー
    (8.60, 9.05, 1.6, 2),    # 稲妻が走る
    (9.05, 9.30, 1.0, 2),    # 白黒インパクトコマ（スナップ）
    (9.30, 9.75, 0.4, 1),    # 衝撃波リング：スロー
    (9.75, 11.05, 2.0, 2),   # 吹き飛び：高速
    (11.05, 11.65, 0.35, 1), # ビル窓ガラス破砕：スロー
    (11.65, 13.00, 1.8, 2),  # 瓦礫：高速
    (13.00, 13.45, 0.6, 1),  # たこさん登場の寄り
    (13.45, 16.30, 1.6, 2),  # 触手の嵐
    (16.30, 17.00, 1.0, 2),
    (17.00, 21.95, 1.9, 2),  # 鉄塔上の高速戦闘
    (21.95, 22.35, 0.45, 1), # 仮面アップ
    (22.35, 24.15, 1.0, 2),  # 最終技の溜め
    (24.15, 24.75, 0.22, 1), # 激突：超スロー
    (24.75, 25.20, 1.0, 2),
    (25.20, 26.20, 0.6, 1),  # 閃光とリング
    (26.20, 30.00, 1.0, 3),  # 余韻
]

WHITE_SRC = [272 / 30, 333 / 30, 757 / 30]
FLICKER_SRC = [(268 / 30, 272 / 30), (728 / 30, 736 / 30)]
SHAKE_SRC = [(97, 0.5), (150, 0.35), (238, 0.5), (272, 0.8), (333, 0.7), (440, 0.4),
             (600, 0.35), (728, 1.0), (757, 1.0)]
FLICKER_MAX_OUT = 8  # スロー中でも点滅は出力8コマまで（強い明滅を避ける）
FLICK_START = {}
RADIAL_SRC = [(90, 97), (180, 238), (660, 728)]
STREAK_SRC = [(97, 135, 1.0), (300, 333, -1.0)]


def build_timeline():
    """出力フレームごとに (元の時刻[秒], step, 区間番号) を返す"""
    tl = []
    acc = 0.0
    for k, (a, b, s, step) in enumerate(SEGMENTS):
        out_len = (b - a) / s
        start = round(acc * FPS)
        acc += out_len
        end = round(acc * FPS)
        for j in range(start, end):
            local = (j - start) / FPS
            if step > 1:  # コマ打ち：出力フレームをstep単位で保持
                local = ((j - start) - ((j - start) % step)) / FPS
            tl.append((min(a + local * s, b - 1e-4), step, k))
    return tl


dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)


def interp(f0, f1, t):
    if t < 1e-3:
        return f0
    g0 = cv2.cvtColor(f0, cv2.COLOR_RGB2GRAY)
    g1 = cv2.cvtColor(f1, cv2.COLOR_RGB2GRAY)
    fw = dis.calc(g0, g1, None)
    bw = dis.calc(g1, g0, None)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    w0 = cv2.remap(f0, xx - fw[..., 0] * t, yy - fw[..., 1] * t, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    w1 = cv2.remap(f1, xx - bw[..., 0] * (1 - t), yy - bw[..., 1] * (1 - t), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return (w0.astype(np.float32) * (1 - t) + w1.astype(np.float32) * t).astype(np.uint8)


def shake_env(sf):
    e = 0.0
    for f, a in SHAKE_SRC:
        if f <= sf < f + 18:
            e = max(e, a * np.exp(-(sf - f) / 5.0))
    return e


def effects(i, f, sf, prev_sf, n_out, title_start):
    f = f.astype(np.float32) / 255.0
    for a, b in RADIAL_SRC:
        if a <= sf < b:
            m = v2.radial_lines(i, 0.85)[..., None]
            f = f * (1 - m) + m * 0.97
    for a, b, d in STREAK_SRC:
        if a <= sf < b:
            m = v2.streak_lines(i, d)[..., None] * 0.8
            f = f * (1 - m) + m * 0.97
    f = v2.bloom(f)
    t, pt = sf / FPS, prev_sf / FPS
    for a, b in FLICKER_SRC:
        if a <= t < b:
            FLICK_START.setdefault(a, i)
        if a <= t < b and i - FLICK_START[a] < FLICKER_MAX_OUT and ((i - FLICK_START[a]) // 2) % 2 == 0:
            g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
            bw = (g < 0.45).astype(np.float32)
            red = np.clip((f[..., 0] - f[..., 1]) * 3, 0, 1)
            f = np.stack([np.maximum(bw, red), bw * (1 - red), bw * (1 - red)], -1)
    for w in WHITE_SRC:
        if pt < w <= t + 1e-6 or (abs(t - w) < 1 / FPS and pt < t and pt < w):
            f = np.clip(f * 0.25 + 0.85, 0, 1)
            break
    e = shake_env(sf)
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
    f = f * v2.VIG
    if i >= title_start:
        alpha = min(1.0, (i - title_start) / 8.0)
        a = v2.TITLE[..., 3:4] * alpha
        f = f * (1 - a) + v2.TITLE[..., :3] * a
    return (np.clip(f, 0, 1) * 255).astype(np.uint8)


def audio_filter():
    parts, labels = [], []
    for k, (a, b, s, _) in enumerate(SEGMENTS):
        chain = f"[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS"
        if s < 1:
            chain += f",asetrate={int(SR * s)},aresample={SR}"
        elif s > 1:
            chain += f",atempo={s}"
        parts.append(chain + f"[s{k}]")
        labels.append(f"[s{k}]")
    parts.append("".join(labels) + f"concat=n={len(SEGMENTS)}:v=0:a=1,"
                 "equalizer=f=70:t=q:w=1:g=5,acompressor=threshold=-14dB:ratio=3:attack=5:release=120,"
                 "alimiter=limit=0.95[a]")
    return ";".join(parts)


def main():
    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(SRC), "-vf", f"scale={W}:{H}:flags=lanczos",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    frames, sz = [], W * H * 3
    while True:
        buf = dec.stdout.read(sz)
        if len(buf) < sz:
            break
        frames.append(np.frombuffer(buf, np.uint8).reshape(H, W, 3))
    dec.wait()
    n_src = len(frames)
    tl = build_timeline()
    n_out = len(tl)
    title_start = n_out - 75
    print(f"output {n_out} frames = {n_out / FPS:.2f}s", flush=True)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", str(SRC), "-filter_complex", audio_filter(),
         "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(OUT)],
        stdin=subprocess.PIPE)
    prev_sf = -1.0
    for i, (t, step, k) in enumerate(tl):
        sf = t * FPS
        i0 = min(int(sf), n_src - 1)
        if step == 1:
            frac = sf - int(sf)
            f = interp(frames[i0], frames[min(i0 + 1, n_src - 1)], frac)
        else:
            f = frames[i0]
        enc.stdin.write(effects(i, f, sf, prev_sf, n_out, title_start).tobytes())
        prev_sf = sf
    enc.stdin.close()
    enc.wait()
    print(OUT)


if __name__ == "__main__":
    main()
