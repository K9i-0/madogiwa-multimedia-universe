# Codex Petsから応用した手法の出典

2026-10-15確認。ユーザーの制作履歴と、OpenAIが提供するPets用スキルの実装を照合。

- [OpenAI公式：Pets / Create a custom pet](https://learn.chatgpt.com/docs/pets#create-a-custom-pet) は、Create petが同梱のhatch-petスキルをインストールすることを説明する。
- ローカル `~/.codex/skills/hatch-pet/SKILL.md` には、連続ポーズのrow-strip生成、`extract_strip_frames.py` による切り出し、組立・プレビューの工程がある。
- 現行 `work-pets/0.1.6/skills/create-pet/SKILL.md` でも連続原画と切り出しを使用。プラグインのauthorはOpenAI。
- MMUで実際に採用した第一弾の原画・組立は `.claude/skills/line-stickers/references/history.md` と `27_LINE_STICKERS/sets/01/` に記録されている。よーたんは3列×2行の原画、そば屋は4採用原画。全員が同じ方式とは説明しない。

動画では「OpenAIが提供するCodex Pets用のスキルを参考に、連続したポーズを一枚に描いて切り出す部分をLINEスタンプへ応用した」と述べる。「OpenAI公式のLINEスタンプ制作法」「OpenAIが発明した手法」とは広げない。

「スプレッドシート」は表計算、「スプライトシート」は複数のコマをまとめた画像。本編では後者の名称を使う。Excel風の画面デザインとは区別する。
