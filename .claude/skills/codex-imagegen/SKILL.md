---
name: codex-imagegen
description: Claude CodeなどCodex以外のハーネスから、ログイン済みCodex CLIの内蔵image_gen（ChatGPTサブスク枠、APIキー不要）で画像を新規生成・参照付き生成・編集し、指定パスへ保存する。他スキルが「imagegen」「Imagegen」「画像生成」を指示していて、自分がCodexではない場合に必ず使用する。Codex上では内蔵のimagegenスキルを直接使うため対象外。
---

# Codex Imagegen（Claudeからの利用）

他スキルの「`imagegen` スキルを使う／読む」という指示は、Claude Codeではこのスキルで実行する。生成の中身（構図・同一性・参照画像の役割・保存先・採否）は呼び出し元スキルの指示に従い、このスキルは**実行経路**だけを担う。

## 方針

- 標準経路は `codex exec` 経由のCodex内蔵 `image_gen`。ChatGPTサブスクの利用枠を消費し、`OPENAI_API_KEY` は使わない。
- API経路（`~/.codex/skills/.system/imagegen/scripts/image_gen.py`、従量課金）、別モデル、SVG/HTMLでの代用へ勝手に切り替えない。ユーザーが明示した場合だけ使う。
- 1枚あたり約30〜40秒・数万tokens相当のサブスク枠を使う。候補数は依頼どおりにし、自動で大量生成しない。
- 生成AIの画像をClaude自身が描いたように扱わず、出力は必ずReadツール等で目視確認してから提示・採用する。

## 実行

```bash
SKILL=.claude/skills/codex-imagegen/scripts/codex_imagegen.py

# 新規生成
python3 $SKILL --prompt-file path/to/prompt.txt --out path/to/out_v1.png

# 参照画像つき（順序が Image 1, 2... になる。役割を必ず添える）
python3 $SKILL --prompt-file prompt.txt \
  --ref 03_SCRIPTS/00_TEMPLATES/characters/character_takosan_basic_sheet.png --ref-label "character identity reference" \
  --ref draft_v1.png --ref-label "edit target" \
  --out path/to/out_v2.png
```

- 引数: `--prompt` または `--prompt-file`、`--ref`（複数可）、`--ref-label`（`--ref`と同順）、`--out`、`--count`（同一プロンプトの別案。別内容は別呼び出し）、`--overwrite`、`--timeout`（既定900秒）、`--model`。
- 結果はJSONで標準出力に出る。`ok: true` なら `outputs` が保存先。`--count` 2以上や複数枚返った場合は `-1`, `-2` の連番になる。
- 既存ファイルは上書きしない。修正は `_v2` 等の別名で保存し、提示済みの版を残す。
- 長いプロンプトや本番プロンプトは `--prompt-file` で渡し、そのファイルを作品ディレクトリに保存する（再現・Studio登録用）。
- スクリプトは `codex exec --json -s read-only` を一時ディレクトリで実行し、`thread.started` の `thread_id` から `~/.codex/generated_images/<thread_id>/` だけを回収する。並行する別Codexセッションの画像は混ざらない。

## プロンプト

呼び出し元スキルの指示を優先し、書式はCodexの `~/.codex/skills/.system/imagegen/SKILL.md`（Shared prompt schema）と `references/prompting.md` を参考にする。

- 各参照画像の役割（同一性の参照／編集対象／スタイル参照）を明記し、編集では「変えるもの」と「変えないもの」を毎回書く。
- 正確な文字は引用符で列挙し、`No other text` を付ける。
- 透過背景は「transparent background」を指示し、出力のアルファを確認する。

## 失敗時

- `ok: false` の `codex_message` と `stderr_tail` を確認する。`codex login status` が `Logged in using ChatGPT` であること、`codex features list` で `image_generation` が `true` であることを確かめる。
- 利用枠超過・規約による拒否などは、内容を短くユーザーへ伝える。API経路への切替は提案に留め、明示の許可なく実行しない。
- 手動で実行する場合、`codex exec` の `-i` は複数の値を受け取るため、プロンプトを `-i` より前に置くか標準入力（`-`）で渡す。
