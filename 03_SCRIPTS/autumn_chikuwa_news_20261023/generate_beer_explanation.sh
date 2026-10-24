#!/bin/bash
# User feedback 2026-10-24: exactly three approved speech takes, one attempt each.
# Existing outputs or attempt markers prohibit accidental retries.
set -euo pipefail
cd "$(dirname "$0")/../.."
p=03_SCRIPTS/autumn_chikuwa_news_20261023
out="$p/remotion/out/beer_explanation_20261024"
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
once anchor_question '旬を迎えた天然のちくわですが、採る際には注意も必要なんですよね。' "$p/voice_forest.wav" 2026 "$anchor"
once expert_explanation 'はい。山には毒ちくわも自生しています。見た目だけでは食用と区別がつきません。毒ちくわ特有のビール臭が、見分ける手がかりになります。' "$p/voice_ref_okayaman_visible.wav" 42
once anchor_response 'こうして並べてみても、見た目ではまったく違いが分かりませんね。では、もう一度、現場に戻ります。' "$p/voice_forest.wav" 2026 "$anchor"
