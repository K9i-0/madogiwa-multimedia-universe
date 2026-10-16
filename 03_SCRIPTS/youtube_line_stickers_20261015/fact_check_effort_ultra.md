# effort Ultra の公式確認

確認日: 2026-10-16（JST）

対象: 本動画の投稿者が使った **GPT 6 Astra / effort Light・Ultra**。別モデルへの置き換えは行わない。

## 結論

「Ultra は、複数のエージェントが作業を分担して並行して進めるモード」という短い補足を追加できる。公式の Models 本文で、Ultra がサブエージェントを使って複雑な作業の別々の部分を並列に処理すると説明されている。同ページは、分割できる大きな作業の加速にも言及している。

ただし、「Ultra だけが複数エージェントを使える」「必ず速い」「トークン・料金も節約できる」とは説明しない。他 effort でも明示的に分担を指示でき、並列化の効果は作業を独立した単位に分けられるかによる。

## 確認した内容

| 論点 | 公式本文から確認できること | 動画での扱い |
| --- | --- | --- |
| Ultra の定義 | Models の「Know when to use Max or Ultra」は、Ultra をサブエージェントによる複雑な作業の並列分担として説明。Max は一つの課題により長く推論する設定として区別している。 | 単に「より深く考える設定」とするより、並列分担を一文補足すると正確。 |
| 他 effort の multi-agent | Subagents の ChatGPT Work 向け説明は、他の intelligence level でも明示的な依頼でサブエージェントを利用できるとしている。ローカル Codex の app / CLI / IDE 向け説明も、直接の依頼または適用される AGENTS.md・skill 指示による分担を説明しており、Ultra 限定とはしていない。 | 「Ultra だけ」「他 effort は必ず単体」とは言わない。 |
| 自発的な分担 | Subagents は ChatGPT Work の Ultra で自発的な委任が可能と明記。一方で現行のローカル Codex の項目は直接依頼やプロジェクト・skill 指示を説明している。 | クライアント差の細部を本編へ増やさず、「並行して進められる」にとどめる。 |
| 速度・効率 | Models は複雑な作業の加速に言及。Subagents は独立して並行できる作業で時間短縮が可能と説明。同時編集は競合や調整負担を増やし得る。 | 「分担できる作業を効率よく進める」と条件付きで言える。常に短時間とは保証しない。 |
| 使用量 | Subagents は、各エージェントがモデル・ツール処理を行うため、同等の単一エージェント実行よりトークンを多く使うと説明。 | 「効率」をトークン節約・料金節約の意味で使わない。 |

## 採用文（v7）

設定紹介の `settings-03` だけを次の文へ変更する。

> 仕上げは、同じモデルのUltraです。複数のエージェントで作業を分担して、並列に進められます。

画面の Ultra 欄は「作業を分担・並列で進める」。下注記は「Codex側の設定です。Imagegenの画質設定とは別です」。

この採用文は、並列分担の公式説明に対応し、速度の絶対保証や Ultra 以外では利用不可という主張を含まない。既存の投稿者の好みによる使い分けという説明も保つ。

## 検討した短い補足案

既存の「案出しは Light、仕上げは Ultra」「投稿者の使い分けであり好みで変えてよい」という説明は維持し、その間に一文を加える。

> Ultra は、複数のエージェントが作業を分担して、並行して進められるモードです。

速度の利点まで含めるなら、次の二文にする。

> Ultra は、複数のエージェントが作業を分担して、並行して進められるモードです。分担できる仕上げ作業を、効率よく進めたいときに使っています。

後半は投稿者の使い分けを述べる文案であり、LINE スタンプ制作に特化した公式の性能保証ではない。動画の主題を保つには一文だけの追加を推奨する。

## 出典と確認手順

OpenAI Docs スキルを読み、利用可能な公式ドキュメント MCP で `GPT 6 Astra effort Ultra` を検索。その後、以下の実ページ本文を `fetch_openai_doc` で取得して確認した。検索結果の抜粋だけを根拠にはしていない。ローカル機能フラグ、モデルカタログ、非公式記事は根拠にしていない。

- [Models — Know when to use Max or Ultra](https://learn.chatgpt.com/docs/models#know-when-to-use-max-or-ultra): Ultra の並列分担と Max との違い。
- [Models — Choose a model](https://learn.chatgpt.com/docs/models): サブエージェントによる複雑な作業の加速、Astra の Light が設定上 low に相当すること、Astra の案内。
- [Subagents — Availability / Triggering subagent workflows / Choosing models and reasoning](https://learn.chatgpt.com/docs/agent-configuration/subagents): 他 effort からの明示的な分担、ChatGPT Work とローカル Codex の説明差、並列化の適性とトークン使用量。

補助確認として [Using GPT-6 — What's new](https://developers.openai.com/api/docs/guides/latest-model#whats-new) も取得した。GPT-6 が multi-agent orchestration を利用できる旨はあるが、API の機能を Codex UI の Ultra と同一視する根拠には用いない。
