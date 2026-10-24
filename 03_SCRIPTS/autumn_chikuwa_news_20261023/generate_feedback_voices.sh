#!/bin/bash
# User feedback 2026-10-24: exactly four requested speech takes, one attempt each.
# Existing outputs or attempt markers prohibit accidental retries.
set -euo pipefail
cd "$(dirname "$0")/../.."
p=03_SCRIPTS/autumn_chikuwa_news_20261023
out="$p/remotion/out/feedback_20261024"
mkdir -p "$out"
export IRODORI_TTS_CHECKPOINT=Aratako/Irodori-TTS-v4-Large
export IRODORI_UNCUT=1 IRODORI_CFG_SCALE_TEXT=5 IRODORI_DURATION_SCALE=1
anchor='落ち着いた地方局ニュース読み。標準語で、明瞭かつ均一な速度、抑制された抑揚で真面目に話す。'
once() {
  local key="$1" text="$2" ref="$3" seed="$4" caption="${5:-}"
  if [ -e "$out/$key.attempted" ]; then
    echo "SKIP: $key already attempted; no automatic retry."
    return
  fi
  date -u > "$out/$key.attempted"
  tools/irodori_speak.sh "$text" "$out/$key.wav" "$ref" "$seed" "$caption" > "$out/$key.log" 2>&1
  echo "Finished requested take: $key"
}
once anchor_to_expert 'ちくわ生物学が専門のおかやまんさん、注意点は？' "$p/voice_forest.wav" 2026 "$anchor"
once okayaman_comparison '食用と非常によく似ていますので、見た目だけで判断しないでください。' "$p/voice_ref_okayaman_visible.wav" 42
once anchor_to_field 'では、もう一度、現場に戻ります。' "$p/voice_forest.wav" 2026 "$anchor"
once sobaya_poison 'ど、どく……。' 02_CHARACTERS/Sobaya_voice.wav 42 '息が詰まり、苦しげにかすれた声で途切れ途切れにつぶやく。'
