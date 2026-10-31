#!/bin/bash
set -euo pipefail
EP="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$EP" rev-parse --show-toplevel)"
mkdir -p "$EP/generated/reedit_voices"
export IRODORI_TTS_CHECKPOINT=Aratako/Irodori-TTS-v4-Large
export IRODORI_UNCUT=1 IRODORI_CFG_SCALE_TEXT=5 IRODORI_DURATION_SCALE=1.0
for line in threat final; do
  if [ "$line" = threat ]; then
    text='お菓子をくれなきゃ、退職しちゃうぞ！'
  else
    text='明日から毎日ハロウィンできますね！'
  fi
  "$ROOT/tools/irodori_speak.sh" "$text" "$EP/generated/reedit_voices/${line}_raw.wav" "$ROOT/02_CHARACTERS/Sobaya_voice.wav" 42
  "$ROOT/tools/sobaya_monsterize.sh" "$EP/generated/reedit_voices/${line}_raw.wav" "$EP/v2_sobaya_${line}.wav"
done
