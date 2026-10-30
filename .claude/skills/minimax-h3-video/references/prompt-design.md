# H3のプロンプトと参照設計

H3向け本文を新規作成・改稿するときに読む。2026-10-28のメガジョッキ編と2026-10-30のBBQ編から得た制作上の判断であり、H3全般の性能評価やWanとの対照実験ではない。設定は[profiles.md](profiles.md)、実際の対応引数・結線は[build_workflow.py](../scripts/build_workflow.py)を正本とする。

## メガジョッキ編で起きたこと

根拠はエピソード [`accidenchua_manners_elearning_2_20261028`](../../../../03_SCRIPTS/accidenchua_manners_elearning_2_20261028/) の実入力・記録。どちらもR2V、480p Turbo、640×480、311フレーム、24fps。

| 版 | 入力と演技 | 観測した結果 |
|---|---|---|
| v1 | キャラシート2枚＋福ギュンの実写写真。卓上の巨大ジョッキを福ギュンが滑らせる。個数・白T・仮面の禁止文を多数記載 | ジョッキが3個になり、そば屋の白Tに乳首状の点。非採用 |
| v2 | 正典から作った場面画像1枚。最初から大小2個を正しい位置に置き、福ギュンは空の手で紹介する | 観察したフレームでは2個と大小差を維持。白Tの小さな黒点は残り、局所補修して採用。発話付近で仮面の口形も変化 |

- 実プロンプト：[v1](../../../../03_SCRIPTS/accidenchua_manners_elearning_2_20261028/prompt_mega_v1.txt) / [v2](../../../../03_SCRIPTS/accidenchua_manners_elearning_2_20261028/prompt_mega_v2.txt)。場面入力：[画像](../../../../03_SCRIPTS/accidenchua_manners_elearning_2_20261028/input_mega_scene_v2.png)。生成条件と採否：[compute-record.json](../../../../03_SCRIPTS/accidenchua_manners_elearning_2_20261028/compute-record.json)。補修：[retouch-record.json](../../../../03_SCRIPTS/accidenchua_manners_elearning_2_20261028/retouch-record.json)。
- v1/v2は画像、動作、本文、seedを変更している。「画像1枚にしたから直った」「長文だから失敗した」「Wan由来だから不安定」と原因を断定できない。
- 両版とも否定文は書いてあった。`EXACTLY`や`NO`の強調を増やすだけで個数・細部・仮面固定を保証できなかった、という観測を次の設計に使う。
- ASRでは2人の台詞を確認したが、声質・自然さ・精密なリップシンクの試聴合格ではない。補修後の完成品だけを見て、生成原本も合格だったと記録しない。

## 1. 動かす前の画を成立させる

物体数、人物の左右、大小差、持ち主が重要な固定会話劇では、**実際に動画へしたい一つの場面画像**を第一候補にする。人物同一性の根拠である正典シート・写真は、その画像の制作と照合に使う。正典からずれた顔を場面画像として採用すると、動画も誤った顔を引き継ぐ。

場面画像で確認するのは、人物の同一性、衣装、物体の数と大きさ、手と物の接触、頭・手・小道具の画面内への収まり。小道具は台詞に登場する時点で突然出現させず、必要な初期状態を写す。今回なら「左に福ギュンと通常ジョッキ、右にそば屋と巨大ジョッキ、計2個」を画で成立させる。

追加の写真・シートは、場面画像で不足する顔や角度を補う場合に使い、各画像の役割を書く。上限9枚を目標にせず、同じ人物の別衣装・別小道具・複数面を無目的に足さない。シートを直接使う場合は、人物同一性の参照であることを明記し、複数面・ラベル・背景を場面の人数や構図として再現させない。

R2Vの場面画像は参照であり、画素単位の初期フレーム固定ではない。`EXACT`という本文だけでI2Vへ変わるわけではない。始点・終点が主目的ならI2Vを検討するが、現行ビルダーの音声参照結線はR2Vのみ。単に画像1枚だからという理由で、音声参照を失うモード変更をしない。

## 2. 動作を状態の変化として書く

各カットについて、台本に次を短く整理してから本文へ展開する。新しい管理ファイルを増やす必要はない。

| 項目 | メガジョッキ編の例 |
|---|---|
| 初期状態 | 2人とも着席。通常1個が左、巨大1個が右。両方とも卓上 |
| 必要な変化 | 福ギュンが空の手で紹介して発話。そば屋が見比べ、少し首を傾けて返答 |
| 維持する状態 | 人数、左右、ジョッキ2個と大小差、そば屋の仮面、肌、衣装 |
| 終了状態 | ジョッキは同じ位置。福ギュンが小さくうなずき、そば屋は戸惑う |

- 「持っている」「卓上に固定」「相手へ渡す」を同時に要求しない。持つ人物、どの手、持ち替え前後、置き場所を整合させる。
- 運搬そのものが必要でない紹介なら、空の手で示す演技にすると接触と持ち主の変化を減らせる。今回の改善案であり、全作品の小道具を卓上固定にする規則ではない。
- 受け渡し・飲酒・移動がユーザーの見せ場なら残す。動作の節目でカットを分ける、始点画像を作るなどで成立を狙う。「安定化」のために勝手に見せ場を静止へ置き換えない。
- 静かな会話劇は一つの場所・画角を第一候補にする。Wan用の「30秒以内なら全場面を一つのリクエストへ」という規則を移植しない。現行ビルダーは5〜362フレーム、`17k+5`、24fps。動作と自然な台詞が収まる範囲で生成単位を決める。

## 3. 本文は参照・状態・演技・音響へ分ける

冒頭で参照の役割と画角を指定し、人物・小道具の初期状態、順序のある演技と台詞、終了状態と必要な音響を続ける。英語の場面記述と日本語台詞は今回の実行例と同じ形式を使える。英語が必ず優れると検証したわけではない。

禁止文は重要な破綻へ絞り、欲しい状態を先に書く。例えば `no extra mugs` の反復だけでなく、`The small mug stays on the table in front of Fukuchan; the large mug stays in front of Sobaya.` と所有と位置を書く。文章量の固定上限は設けないが、同じ禁止の重複、本文内の矛盾、今回に関係しない他作品の制約は除く。

キャラクター固有の要件は削らない。

- 福ギュンは[肌と年齢感の基準](../../../../02_CHARACTERS/references/fukuchan-skin-standard.md)を読み、顔同一性に加え、綺麗な肌と自然なシワ・年齢感の両方を残す。基準文の要点を実際の参照へ対応させる。
- そば屋は[人物設定](../../../../02_CHARACTERS/01_Sobaya.md)と最新シートを使う。白Tの胸筋・布のシワを残し、乳首状の局所的な点・突起を除く。厚手の服や全胸の平滑化へ自動変更しない。手や小道具の遮蔽は構図上自然な場合だけ使い、見えている部分の監査は残す。白Tの本文は下記の[BBQ編の採用文面](#白tの点状陰影bbq編の比較)を第一候補にする。
- 仮面は、頭全体の動きと仮面表面の変形を区別する。「仮面の内側から声が聞こえる。仮面は装着したまま、描かれた口は動かない。反応は首・姿勢で示す」と書く。`animate lips, jaw and cheeks` を全員へ一括指定しない。今回のv2も完全な剛体維持は達成していないため、これで解決済みとは扱わない。

## 白Tの点状陰影：BBQ編の比較

白Tの指定は、禁止語を増やす前に、服の素材・連続した表面・照明・シワを具体的に書く。次の文面はBBQ編で採用した実入力。参照番号は実際の場面画像に合わせ、体形・服のフィット感はその画像を維持する。

```text
His fitted white crew-neck T-shirt is a plain, undecorated garment. Its front is one uninterrupted opaque white cotton surface, with a subtle fabric grain, broad soft lighting gradients and natural fabric folds matching Picture 1. The shirt keeps this same material and appearance throughout all movement.
```

[比較計画](../../../../03_SCRIPTS/bbq_doku_chikuwa_h3_20261030/shirt_test_plan_v1.json)では、場面画像・音声3本・seed 2026103001・362フレーム・864×480・24fps・Turbo 8stepを固定して3案を生成した。基準版とは別のA100セッションであり、ビット単位の決定性は保証しない。

| 案 | 主な変更 | 原本の観測結果 |
|---|---|---|
| positive_cloth（上記） | 白Tの禁止文を、不透明な白い綿布・微細な織り・広い柔らかな陰影・自然なシワの指定へ置換 | 目立つ対の黒点が見られず、体形と布のシワを保持。採用 |
| garment_reference | 参照画像どおりの服・均一な白い布の維持を強調 | 点状陰影が再発。非採用 |
| reference_only | 短い白布指定に加え、筋肉の形容を参照シルエットへの指定へ変更 | 点状陰影が再発。非採用。白Tの一文だけを変えた比較ではない |

採用文面は乾杯・発覚・転倒にも適用し、各カットの画像・音声・seed・設定は元の版から維持した。冒頭を含む4カットの連続サンプルと胸元の拡大・原寸フレームで改善を確認し、完成v2は胸元の局所補修なし。食事カットは初版の原本を使用した。実プロンプト・原本ハッシュ・確認範囲は[比較結果](../../../../03_SCRIPTS/bbq_doku_chikuwa_h3_20261030/shirt_prompt_experiment_report.json)、採用後の構成は[制作記録](../../../../03_SCRIPTS/bbq_doku_chikuwa_h3_20261030/production-report.json)を参照。

3案とも乳首を指す禁止語は除いているので、「その語を消すだけで直る」とは言えない。モデル内部の補正機構や、他作品・任意seedへの普遍的効果も未検証。キャラクターシートの微小な色差が原因と決めつけず、実際にH3へ渡した画像と生成原本を比較する。白Tが改善しても、仮面の口の変形・余分な発話・再度食べる動作は別問題として確認する。

## 4. 音声の役割と発話順を固定する

`--image`と`--audio`の接続順がそれぞれ`<Picture 1>`、`<Audio 1>`になる。本文とworkflowを照合する。今回のように採用台詞WAVを使うなら、音声番号、話者、台詞全文を一組にし、`<d>[Japanese] 台詞</d>`を実行例として使う。タグは本文の表現であり、別の強制同期パラメータではない。

- 今回の台詞を収録したWAVと、別の台詞の声質参照を区別する。前者へWan用の`voice-timbre only; do not copy its words`をそのまま付けない。後者は今回の台詞全文を別途明記する。
- 各行は誰が話すか、誰が聞くか、次に誰が話すかを書く。同時発話が必要な場面以外は、先の話者が終わってから次へ進める。
- 生成尺は採用音声の実測長と必要な反応の間から計画する。通常会話の本文では発話順と自然な話速を中心にし、ミリ秒単位の窓を要求しない。ユーザー指定の厳密なキューは保持して別途監査する。
- R2Vへ渡した音声の波形、尺、開始時刻がそのまま出るとは保証しない。字幕は予定時刻で確定せず、H3が生成した音声から測る。可視発話を参照WAVで全面置換しただけで同期済みとしない。
- 教材UI、字幕、別画面の解説ナレーション、導入BGM、DVD風の画質加工は、今回のように編集で組み立てられる。H3には芝居に必要な照明・美術・演技を指定する。ユーザーが一体生成を求めた場合はその指定を優先する。Wan専用の音声生成元制限は自動継承しない。

## 改稿例：メガジョッキ編

以下はメガジョッキ編の反省とBBQ編の白T採用文面を反映した**未生成の次回用例**。v2の実送信履歴を上書きせず、再利用時には入力と台詞を今回のものへ合わせる。画角4:3・約13秒・人物2人・ジョッキ2個はこの例の条件であり、全作品の既定ではない。

入力対応：`<Picture 1>` = 正典と照合済みの場面画像、`<Audio 1>` = 福ギュンの今回の台詞、`<Audio 2>` = そば屋の今回の台詞。生成設定は640×480、311フレーム、24fpsを想定。

```text
A single continuous live-action Japanese employee-training skit, about 13 seconds, 4:3. Use <Picture 1> for the scene composition, character appearances, costumes and props. Locked eye-level medium two-shot, plain izakaya lighting and understated acting.

Fukuchan sits on the left and Sobaya on the right, matching the reference identities. Fukuchan retains the same facial structure, clean even complexion and natural skin texture, including forehead and eye-area lines, smile lines and nasolabial folds. Keep the reference's apparent age and expression changes; do not add blemishes, freckles or rough pores, erase wrinkles, reshape his face or create waxy skin. Preserve natural lighting and facial shading.

Sobaya retains his broad muscular silhouette, short black hair, neutral gray exposed skin and opaque white mask with black eye holes, red markings and a black forehead dot. His fitted white crew-neck T-shirt is a plain, undecorated garment. Its front is one uninterrupted opaque white cotton surface, with a subtle fabric grain, broad soft lighting gradients and natural fabric folds matching Picture 1. The shirt keeps this same material and appearance throughout all movement. His mask stays fitted; its painted mouth and surface stay unchanged when his head moves. His voice comes from behind the mask; his reactions are conveyed by head and body gestures.

There are two beer mugs already resting on the table: one ordinary small mug in front of Fukuchan and one giant mug, more than twice its height, in front of Sobaya. Both mugs remain in these positions, with the same size, contents and handles. Fukuchan's presenting hand is empty. Sobaya rests a hand by the giant mug's handle. Keep both heads and both mugs fully in frame.

Fukuchan makes a small open-palm gesture toward the giant mug and says once: <d>[Japanese] そば屋さんには、こちらをご用意しました。</d> <Audio 1> is Fukuchan's voice and spoken-line reference. Sobaya listens silently.

After Fukuchan finishes, he closes his mouth and listens. Sobaya looks at the giant mug, then toward Fukuchan with a small puzzled head tilt, and says once from behind his unchanged mask: <d>[Japanese] なんで、僕だけこんなに大きいんですか。</d> <Audio 2> is Sobaya's voice and spoken-line reference. Fukuchan does not mouth Sobaya's line.

Speak at a natural conversational pace. Then Fukuchan gives a small courteous nod; Sobaya holds the puzzled pose. End with both seated and both mugs still on the table. Only these two lines and quiet room tone. No additional people or mugs, lifting or passing the mugs, narration, music, captions or UI.
```

## 生成後の判定と改稿

原本で、冒頭・重要動作の前後・発話中・終端を確認する。特に物体数と大きさ、手の接触、人物同一性、仮面、白Tを参照と比較する。細かな点を判定するときはコンタクトシートだけで済ませず、該当原寸フレームも見る。ASRの文言確認と、音声の試聴・口パク確認は別に記録する。

| 観測した破綻 | 次に検討する修正 |
|---|---|
| 小道具が増える／持ち主が曖昧 | 場面画像の初期配置、本文の接触・受け渡し状態を確認。禁止文だけ増やさない |
| 動作が多く、順序や身体が崩れる | 必須の見せ場を残し、不要な同時動作を減らすか動作の節目で分割 |
| 参照画像の時点で顔・手・服が違う | 動画本文で押し切らず、まず入力画像を正典へ直す |
| 画像は正しいが仮面や身体が途中で変形 | 発話・表情指示との矛盾を除き、区間と状態を特定。完全固定は未達として記録 |
| 白Tだけに小さな点が残る | 原寸で発生区間と実入力を確認。上記の白い綿布指定を候補にし、比較時は画像・音声・seed・設定を固定する。局所補修を選ぶなら範囲と前後を記録し、人物・衣装全体を変えない。今回の補修座標を別動画へ流用しない |
| 台詞の欠落・重複・話者の入れ替わり | 音声番号、実入力、台詞全文、発話順、尺を照合。ASRだけで自然さを合格にしない |

再生成する場合は失敗箇所、狙う修正、入力・本文・seed・設定の変更点を記録する。原因比較なら主要因を絞り、複数変更した制作改善なら因果検証済みと書かない。seed変更や禁止文の追加だけで盲目的に繰り返さず、同じ破綻が続けば入力・動作・分割・編集の設計へ戻る。既存の生成許可範囲を超えてGPUジョブを追加しない。プロンプトを更新したこと自体を、改善が実生成で確認されたことと混同しない。
