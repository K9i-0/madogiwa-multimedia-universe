#!/bin/bash
# 編集v1: 720p Lanczos拡大 + インパクト時の減衰する画面揺れ・色ずれ + 効果音の低音強化（Wan生成音のみ使用、合成音なし）
set -euo pipefail
cd "$(dirname "$0")"
IN=wan3_sakuga_v1_seed110101_480p.mp4
OUT=final_sakuga_edit_v1_720p.mp4
# 衝撃時刻（生成動画の目視・音声ピークから）: 突進3.0 / 拳命中7.95 / ビル貫通10.4 / 最終激突25.0
SHAKE="0"
for a in 3.0 7.95 10.4 25.0; do
  SHAKE="$SHAKE+if(between(t\,$a\,$a+0.6)\,1\,0)*exp(-(t-$a)*6)"
done
ffmpeg -v error -y -i "$IN" -filter_complex "
[0:v]scale=1344:756:flags=lanczos,
crop=1280:720:x='32+28*sin(t*97)*($SHAKE)':y='18+18*cos(t*83)*($SHAKE)',
rgbashift=rh=-6:bh=6:enable='between(t,7.95,8.25)+between(t,25.0,25.35)+between(t,3.0,3.15)',
eq=contrast=1.06:saturation=1.08,unsharp=5:5:0.4,format=yuv420p[v];
[0:a]equalizer=f=70:t=q:w=1:g=5,acompressor=threshold=-14dB:ratio=3:attack=5:release=120,alimiter=limit=0.95[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -crf 17 -preset medium -r 30 -c:a aac -b:a 192k "$OUT"
echo "$OUT"
