#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
p=03_SCRIPTS/autumn_chikuwa_news_20261023
out="$p/remotion/out/coherent_expert_20261024"
mkdir -p "$out"
if [ -e "$out/anchor_intro.attempted" ]; then
 echo 'Already attempted. No automatic retry.'
 exit 0
fi
date -u > "$out/anchor_intro.attempted"
export IRODORI_TTS_CHECKPOINT=Aratako/Irodori-TTS-v4-Large
export IRODORI_UNCUT=1 IRODORI_CFG_SCALE_TEXT=5 IRODORI_DURATION_SCALE=1
tools/irodori_speak.sh '旬を迎えた天然のちくわですが、採る際には注意も必要です。ちくわ生物学が専門の、窓際大学のおかやまん准教授に伺います。' "$out/anchor_intro.wav" "$p/voice_forest.wav" 2026 '落ち着いた地方局ニュース読み。標準語で、明瞭かつ均一な速度、抑制された抑揚で真面目に話す。' > "$out/anchor_intro.log" 2>&1
