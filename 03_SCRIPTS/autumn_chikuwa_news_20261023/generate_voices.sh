#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
p=03_SCRIPTS/autumn_chikuwa_news_20261023
export IRODORI_UNCUT=1 IRODORI_CFG_SCALE_TEXT=5 IRODORI_DURATION_SCALE=1
export IRODORI_TTS_CHECKPOINT=Aratako/Irodori-TTS-v4.1-Small
caption='落ち着いた地方局ニュース読み。標準語で、明瞭かつ均一な速度、抑制された抑揚で真面目に話す。'
tools/irodori_speak.sh '秋の味覚、ちくわ狩りが最盛期を迎えています。' "$p/voice_forest.wav" 02_CHARACTERS/YumeTeleAnchor_voice.wav 2026 "$caption"
tools/irodori_speak.sh '食用と非常によく似ていますので、見た目だけで判断しないでください。' "$p/voice_comparison.wav" 02_CHARACTERS/Okayaman_voice.wav 42
tools/irodori_speak.sh '中継をいったん失礼します。' "$p/voice_interruption.wav" 02_CHARACTERS/YumeTeleAnchor_voice.wav 2026 "$caption"
