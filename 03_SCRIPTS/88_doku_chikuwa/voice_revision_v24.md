# v24 セリフ音声比較（2026-10-08）

ユーザー依頼：「88のセリフを今回の方法で作り直してみて」。87「窓際お嬢様部」で採用された福ギュンのSeed-VC方式と、やめ太郎後半のIrodori Large＋短い演技指示を88へ応用する。88にやめ太郎は登場しないため、後者はよーたんへ適用。そば屋は従来のLarge＋monsterizeで新しいテイクを作る。

対象は完成v23の8セリフ。台詞本文は現行を維持し、候補は`.local/doku-chikuwa-voice-v24/`に保存。完成動画・採用音声・Studioは変更しない。

- 福ギュン：report / message / abbreviation / warning の4本。元の発話と間を使い、正典`Fukuchan_voice.wav`を参照してSeed-VCで声質変換。abbreviationは現行動画のWan生成音声。残る3本は追加・変更された文面に対応するWan音声がないため、現在の採用Irodori音声を変換元にする。全4本がWan由来とは扱わない。
- よーたん：deduction / question / reaction の3本。正典`Yotan_voice.wav`、Irodori v4-Large、seed100、本文CFG5、生成尺倍率1、末尾トリムなし。演技指示はそれぞれ「真剣に推理を述べる。落ち着いた自然な会話。」「声を張らず、素で困惑する。」「小声で戸惑い、少し引いている。」。
- そば屋：「これ、毒ちくわです。」を正典`Sobaya_voice.wav`、Large、seed42、本文CFG5、生成尺倍率1、caption「得意げに、当然の事実として言い切る。」で1回生成し、通常の`sobaya_monsterize.sh`を1回適用。

Seed-VC：50steps、length-adjust1、CFG0.7、F0条件あり、auto-F0-adjustあり、fp16なし。4本を1秒無音で区切って処理し、元のサンプル位置で分割。推論後にセリフを早送り・時間伸縮しない。既存Seed-VC環境のshape mismatch警告はログへ保持する。

比較ページは前回版と今回の改善候補を左右に並べ、各音声を定数ゲインで-18LUFS目標・ピーク-1dB以下へ調整。再生時は他の音声を停止。全セリフを順番に聴ける音声も用意する。TTSは各設定1回。ASRに基づく自動再生成・発音の合格判定は行わず、実際の声質・自然さはユーザーの試聴評価と区別する。

実行スクリプトは`.local/doku-chikuwa-voice-v24/prepare.py`、`generate_tts.sh`、`build.py`。生成ログは同ディレクトリ。最終的な秒数・入力・設定・ハッシュは`voice_comparison_v24.json`へ記録する。
