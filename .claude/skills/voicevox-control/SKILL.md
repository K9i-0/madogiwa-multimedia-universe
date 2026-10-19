---
name: voicevox-control
description: VOICEVOXの音声生成、読み間違い修正、共有読み辞書、話者・速度・間・アクセント、AudioQueryと音声キャッシュを管理する。VOICEVOXの誤読、発音、辞書登録、読み上げ制御、既存セリフの再生成を頼まれたときに使用する。解説・怪談・Shorts等の動画形式を問わず使う。台本・資料画面はvoicevox-explainer等の制作スキル、映像編集・ミックス・レンダーはremotion-videoへ渡す。
---

# VOICEVOX音声制御

字幕用の原文と音声用の読みを分け、同じ誤読を次の作品へ持ち越さない。音声だけの依頼にもこのスキルを使う。

## まず採用設定を確認する

- 既存作品では採用版の生成コード・クエリ・設定を読む。ユーザー指定を優先し、話者、スタイル、速度を読み修正のついでに変えない。
- 窓際族の配役は [VOICE_CAST.md](../../../02_CHARACTERS/VOICE_CAST.md) を正本とする。VOICEVOX指定のないメンバーを一律にVOICEVOXへ替えない。解説テンプレの速度1.1等を怪談・他話者へ流用しない。
- エンジンの稼働状態、`/version`、`/speakers` を確認する。APIの `speaker` はスタイルID。起動・クエリ操作・キャッシュは [engine.md](references/engine.md) を参照する。

## 読みを準備する

1. [共有読み辞書](references/readings.json) と [辞書の使い方](references/pronunciation.md) を使う。新しい作品や読み修正では、既存の作品専用 `.replace()` をそのまま複製せず、共有ヘルパーを生成処理へ組み込む。
2. 字幕の `text` は維持する。自動補正できる語句から `speech` を作り、`/audio_query` には `speech` を渡す。固有名詞・技術語・作品固有の略称は必要なscopeだけ有効にする。
3. `人・方・空・杯・分・行・間・弦・通って` 等は前後の意味を読む。一文字の全置換をしない。辞書の確認候補とクエリの実際の読みを照合し、必要な行だけ `speech_override` で指定する。例：空の缶＝から、空の色＝そら、来る方＝かた／ほうの両方があり得る。
4. 行全体の明示的な読みを最優先し、さらに共有辞書を掛けて書き換えない。既存の `voicevoxReading` / `reading` を使う実装では、採用済みの意味を確認して `speech_override` へ渡す。混在台本のIrodori等の行には適用しない。

リポジトリルートからの準備例（Python標準ライブラリのみ）：

```sh
python3 .claude/skills/voicevox-control/scripts/prepare_readings.py \
  --input /tmp/voicevox-lines.json --output /tmp/voicevox-prepared.json \
  --scope mmu --scope tech
```

入力は `[{"id":"line-01","text":"管理人が祠を見た。"}]` のようなJSON配列。出力には原文、`speech`、適用語句・文脈確認候補・辞書hashを残す。既存の生成スクリプトへ読み込み方を合わせる例は [pronunciation.md](references/pronunciation.md) にある。

## 生成と確認

1. 読みを直した `speech` から `/audio_query` を作り直す。**`query.kana` だけを編集しても合成音声は変わらない**。アクセントを直接直す場合は [engine.md](references/engine.md) の手順で `accent_phrases` を更新する。
2. 採用済みの速度・音高・抑揚・無音長を設定し、最終クエリを保存して合成する。キャッシュは最終クエリと話者・エンジン情報から識別する。字幕が同じでも読みが変わった音声を再利用しない。
3. 修正語、その前後、固有名詞、数詞・助数詞、文脈確認候補の `kana` / `accent_phrases[].moras[].text` を点検する。可能なら文全体を試聴し、発音・アクセント・間を確認する。ASR一致やかな確認だけで聴感まで合格にしない。未試聴ならその範囲を記録する。
4. 実測したWAV尺からタイムラインを更新する。尺合わせの早回しや音素の切り貼りを読み修正の代わりにしない。動画への反映は [remotion-video](../remotion-video/SKILL.md) へ渡す。

## 誤読が見つかったら蓄積する

- 同じ回の同じ語を検索し、字幕ではなく発音を修正する。採用が確認できた読み・適用条件・出典を辞書へ記録する。
- 読みが固定できる語は `replacements`、意味で変わる語は `context_checks`。作品限りの略称は専用scopeまたは作品内の辞書、行に依存する読みは `speech_override` にする。
- 対象の例と、変更してはいけない例を両方確認する。辞書の回帰確認は `python3 .claude/skills/voicevox-control/scripts/test_prepare_readings.py`。
- 共有JSONは作品側の読み準備用。エンジン常設の `/user_dict` とは別物で、自動インポートしない。常設辞書の編集を依頼された場合の手順は [engine.md](references/engine.md) を参照する。
