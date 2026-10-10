# UMA呼称と演出の区別

2026-10-10確認。

- ビッグフット：北米西部にいると伝えられる毛深い類人猿状の存在。一般的な伝承説明のみ使用。[Oxford Learner’s Dictionaries](https://www.oxfordlearnersdictionaries.com/us/definition/english/bigfoot)
- イエティ：ヒマラヤにいると伝えられる毛深い人型の存在。一般的な伝承説明のみ使用。[Cambridge Dictionary](https://dictionary.cambridge.org/us/dictionary/english/yeti)

上記のUMAが実在すると断定しない。SOBAYAとの比較、絶滅原人生存説、類人猿説、旧文明説、地球外起源説、学派間の対立は本作の創作。現実の研究者の発言として帰属させない。

広域未確認生物研究所、狭間文明研究所、真壁教授、未確認ニュースネットは架空。報道・論文・照会結果の画面は、正確な文字をReactで描画した本作用の資料。

# シルエット

- 生成方法：内蔵 image_gen、参照付き、透明背景。
- プロンプト：`inputs/silhouette_prompt.txt`
- 採用画像：`inputs/sobaya_silhouette_v2.png`
- 参照：`03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png`
- フルカラーのそば屋を新しい猿人へ変えるのでなく、同一の体格・髪型・仮面の外形を黒く隠した。正体判明前の詳細は台詞と注釈のみ。
- 生成原本：`/Users/kotahayashi/.codex/generated_images/01a1252e-3fee-79a1-9ec0-c0c81af4575e/exec-39bd06ec-917e-443f-9d37-395576629bff.png`

# 証拠映像

元動画を改変せず、低解像度、ぼけ、減色、ノイズの派生MP4を用意。React側で手ぶれ、前景の遮蔽、走査線、信号抜け、受領映像の反復再生を重ねる。手持ち目撃映像と固定観測カメラを区別する。クリーンな既存エピソードの画は `employee` 以降にのみ使用する。

カット元・時刻・フィルター・SHA-256は `evidence_sources_v2.json`、実装は `remotion/prepare_evidence.py` と `remotion/src/Evidence.tsx`。


## v3 採用生成画像

内蔵image_genで新規生成。実際の入力は `inputs/imagegen_v3_prompts.json`。画像内に正確な文字を描かせず、ラベルはRemotionで合成。

- `inputs/bigfoot_v3.png` — SHA256 `76e293a25c0875969b07475ab60cc0d41cc6c3b3b14dc2b41d175ea7af9a60e6`
- `inputs/yeti_v3.png` — SHA256 `aa27e18ff3dd24cbebf0f2a98917468a98c5fa0313492169ce53369c4f7b95b2`
- `inputs/ancient_chamber_v3.png` — SHA256 `d4c3d086280f95b7bd53992f0ee0a8cbd30ee4418b48cd9219571da136177c10`
- `inputs/research_desk_v3.png` — SHA256 `4d5d2f4fe3a1534a9016fb1d3bb81c2d023b030fe0a93b84397488db51f7cef5`

ビッグフット・イエティは伝承の想像復元図、地下構造物は霜重研究員の仮説による想像復元、解析机は林研究員の作業再現として表示。実在の写真資料とは扱わない。
