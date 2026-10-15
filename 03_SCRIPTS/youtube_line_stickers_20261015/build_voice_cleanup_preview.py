#!/usr/bin/env python3
"""Build a short before/after review from the ACTUALLY ADOPTED voice cuts.

Requires Python + NumPy + Pillow, FFmpeg/ffprobe, and the macOS Hiragino font.
The narration sources are never modified. Each before/after pair receives one
shared constant gain computed from the original file, avoiding independent
normalization that would exaggerate differences. No BGM, time stretch, new
voice generation, or additional fades are applied. Cards and the review video
are derived review artifacts, distinct from the final explainer composition.
"""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import unicodedata
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
OUT = P / "remotion/out/voice-cleanup-preview"
FPS, SR, WIDTH, HEIGHT = 30, 48000, 1280, 720
FRAME_SAMPLES = SR // FPS
GREEN, INK, PURPLE = "#176b47", "#182f24", "#8950c8"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def load_wav(path):
    with wave.open(str(path)) as wav:
        assert wav.getsampwidth() == 2 and wav.getframerate() == SR
        channels = wav.getnchannels()
        return np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").reshape(-1, channels).mean(axis=1) / 32768


def shared_gain(source, samples):
    measured = run(["ffmpeg", "-v", "info", "-i", str(source), "-af",
                    "loudnorm=I=-18:TP=-2:LRA=11:print_format=json", "-f", "null", "-"])
    meter, _ = json.JSONDecoder().raw_decode(measured.stderr[measured.stderr.rfind("{"):])
    integrated = float(meter["input_i"])
    peak_db = 20 * math.log10(max(float(np.max(np.abs(samples))), 1e-12))
    gain_db = min(-18 - integrated, -2 - peak_db)
    assert math.isfinite(gain_db)
    return 10 ** (gain_db / 20), {"originalIntegratedLUFS": integrated,
                                 "originalPeakDbfs": peak_db, "gainDb": gain_db,
                                 "policy": "One constant gain from original, applied identically to both versions; target -18 LUFS, peak ceiling -2 dBFS."}


FONT_PATH = next(path for path in Path("/System/Library/Fonts").glob("*.ttc")
                 if unicodedata.normalize("NFC", path.name) == "ヒラギノ角ゴシック W6.ttc")


def font(size):
    return ImageFont.truetype(str(FONT_PATH), size)


def centered(draw, text, y, size, fill):
    f = font(size)
    width = draw.textlength(text, font=f)
    assert width <= 1160, (text, width)
    draw.text(((WIDTH - width) / 2, y), text, font=f, fill=fill)


def wrap(draw, text, size=43, width=1080):
    f = font(size)
    lines, current = [], ""
    for char in text:
        if draw.textlength(current + char, font=f) > width and current:
            lines.append(current)
            current = char
        else:
            current += char
    if current:
        lines.append(current)
    assert len(lines) <= 2
    return lines


def card(cut, before, samples, original_duration, index, total):
    image = Image.new("RGB", (WIDTH, HEIGHT), "#fbfcfa")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 76), fill=GREEN)
    draw.text((48, 20), "やめ太郎の音声修正  /  聴き比べ", font=font(29), fill="white")
    draw.text((1110, 23), f"{index} / {total}", font=font(25), fill="white")
    label = "修正前" if before else "修正後"
    color = "#68766c" if before else GREEN
    draw.rounded_rectangle((490, 111, 790, 180), radius=8, fill=color)
    centered(draw, label, 120, 38, "white")
    centered(draw, cut["id"], 194, 23, "#657167")
    lines = wrap(draw, cut["expectedText"])
    for i, line in enumerate(lines):
        centered(draw, line, 258 + i * 61 - (15 if len(lines) > 1 else 0), 43, PURPLE)
    keep = (cut["keepEndSample"] - cut["keepStartSample"]) / SR
    classification = "長く伸びた語尾を整理" if cut["classification"] == "excess_sustained_vowel" else "発話後の余分な音を整理"
    centered(draw, f"{original_duration:.2f}秒 → {keep:.2f}秒  ／  {classification}", 395, 27, INK)
    # Same time/amplitude axes for a pair. The orange area denotes the removed
    # tail, while the actual adopted fade is represented by the after waveform.
    x0, x1, y0, y1 = 100, 1180, 468, 590
    draw.rectangle((x0, y0, x1, y1), fill="white", outline="#c8d2ca", width=2)
    cut_x = x0 + keep / original_duration * (x1 - x0)
    if before:
        draw.rectangle((cut_x, y0 + 2, x1 - 2, y1 - 2), fill="#fff0d7")
    middle = (y0 + y1) / 2
    draw.line((x0, middle, x1, middle), fill="#d5ddd6")
    # Sparse min/max envelope keeps every transient visible at this resolution.
    span_samples = max(1, round(original_duration * SR))
    for pixel in range(x1 - x0):
        start = round(pixel / (x1 - x0) * span_samples)
        end = round((pixel + 1) / (x1 - x0) * span_samples)
        segment = samples[start:min(end, len(samples))]
        if len(segment):
            low, high = float(segment.min()), float(segment.max())
            draw.line((x0 + pixel, middle - high * 55, x0 + pixel, middle - low * 55), fill=color)
    draw.line((cut_x, y0, cut_x, y1), fill="#b77826", width=2)
    draw.text((100, 600), "0秒", font=font(20), fill="#657167")
    draw.text((1080, 600), f"{original_duration:.2f}秒", font=font(20), fill="#657167")
    centered(draw, "各ペアは同じ音量係数  /  BGMなし  /  比較間隔 0.5秒", 659, 22, "#657167")
    path = OUT / f"card-{index:02d}-{'before' if before else 'after'}.png"
    image.save(path)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cleanup_path = P / "remotion/voice_cleanup.json"
    cleanup = json.loads(cleanup_path.read_text())
    adopted = {row["id"]: row for row in json.loads((P / "adopted_audio.json").read_text())["audio"]}
    cut_count = len(cleanup["cuts"])
    assert cut_count > 0
    audio, segments, pairs, cursor = [], [], [], 0
    hashes = {}
    for index, cut in enumerate(cleanup["cuts"], 1):
        before_path = P / cut["source"]
        after_path = P / adopted[cut["id"]]["file"]
        hashes[before_path] = sha(before_path)
        hashes[after_path] = sha(after_path)
        assert hashes[before_path] == cut["sourceSha256"]
        assert hashes[after_path] == cut["expectedOutputSha256"] == adopted[cut["id"]]["sha256"]
        before_audio, after_audio = load_wav(before_path), load_wav(after_path)
        assert len(after_audio) == cut["keepEndSample"] - cut["keepStartSample"]
        gain, meter = shared_gain(before_path, before_audio)
        pairs.append({"id": cut["id"], "text": cut["expectedText"], "classification": cut["classification"],
                      "before": {"file": str(before_path.relative_to(P)), "sha256": hashes[before_path], "duration": len(before_audio) / SR},
                      "after": {"file": str(after_path.relative_to(P)), "sha256": hashes[after_path], "duration": len(after_audio) / SR},
                      "sharedGain": meter})
        for label, samples in [("before", before_audio), ("after", after_audio)]:
            sound = samples * gain
            assert float(np.max(np.abs(sound))) < 1
            # Every interval ends with at least 0.5 seconds of silence, aligned
            # to whole output video frames for deterministic concatenation.
            frames = math.ceil((len(sound) / SR + .5) * FPS)
            block = np.pad(sound, (0, frames * FRAME_SAMPLES - len(sound)))
            audio.append(block)
            png = card(cut, label == "before", sound, len(before_audio) / SR, index, cut_count)
            segments.append({"id": cut["id"], "version": label, "startFrame": cursor,
                             "durationInFrames": frames, "audioSeconds": len(sound) / SR,
                             "silenceSeconds": frames / FPS - len(sound) / SR,
                             "card": str(png.relative_to(P))})
            cursor += frames
    joined = np.concatenate(audio)
    wav_path = OUT / "comparison.wav"
    with wave.open(str(wav_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes((np.clip(joined, -1, 1) * 32767).astype("<i2").tobytes())
    concat_path = OUT / "cards.txt"
    concat_lines = []
    for segment in segments:
        concat_lines.extend([f"file '{Path(segment['card']).name}'", "option framerate 30", f"duration {segment['durationInFrames'] / FPS:.9f}"])
    concat_lines.extend([f"file '{Path(segments[-1]['card']).name}'", "option framerate 30"])
    concat_path.write_text("\n".join(concat_lines) + "\n")
    video = P / "preview_voice_cleanup.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path),
         "-i", str(wav_path), "-vf", "fps=30,tpad=stop_mode=clone:stop_duration=0.2",
         "-frames:v", str(cursor), "-t", str(cursor / FPS), "-c:v", "libx264", "-threads", "2",
         "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-ar", str(SR), "-movflags", "+faststart", str(video)])
    probe = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(video)]).stdout)
    vs = next(row for row in probe["streams"] if row["codec_type"] == "video")
    assert (vs["width"], vs["height"], vs["r_frame_rate"], int(vs["nb_read_frames"])) == (WIDTH, HEIGHT, "30/1", cursor)
    run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"])
    for path, original_hash in hashes.items():
        assert sha(path) == original_hash
    record = {"video": video.name, "sha256": sha(video), "durationSeconds": cursor / FPS,
              "frames": cursor, "resolution": [WIDTH, HEIGHT], "fps": FPS, "audioSampleRate": SR,
              "sourceCleanupRecord": str(cleanup_path.relative_to(P)), "sourceCleanupSha256": sha(cleanup_path),
              "sourceAudioModified": False, "subjectiveListening": False,
              "normalization": "Within each pair, both use identical constant gain measured from the uncut original; no independent loudness normalization.",
              "scope": f"Review of {cut_count} adopted cuts without BGM. Full explainer mix has its own recorded normalization.",
              "pairs": pairs, "segments": segments, "fullDecode": "passed", "cardVisualReview": "pending"}
    (P / "voice_cleanup_preview.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"video": video.name, "seconds": cursor / FPS, "frames": cursor, "pairs": len(pairs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
