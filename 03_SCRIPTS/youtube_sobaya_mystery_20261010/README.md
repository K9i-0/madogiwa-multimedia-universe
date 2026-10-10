# めたんのミステリー研究所：SOBAYA

## 現行版 v6

ユーザーFBに基づき全パートを見直し。10分33.567秒、1280×720・30fps、116発話。

- 完成動画：`final_remotion_sobaya_mystery_v6.mp4`（ローカル保持）。
- 改修部の抜粋：`preview_changes_v6.mp4`（モニター比較・アトランティス比較・一度だけの映画ネタ・円筒の応答）。
- 正本台本：`script.md`。発話と間：`remotion/dialogue.json`。
- パート別の改善記録：`part_review_v6.md`。
- タイミング：`remotion/src/edit-manifest.json`。字幕：`subtitles_ja.srt`。章：`chapters.txt`。
- 素材と出典：`research_sources.md`、`inputs/`。

古代文明パートは「アトランティスも容器も水の中」、宇宙パートは「秘密施設もSOBAYAも中身が分からない」「ちゃぷちゃぷを応答と認定」に整理。研究者の推論ミスが短く伝わる比較図を加えた。余分な学説の分岐・推進器官の説明・三説の統合を削った。

映画・アニメの参照は『天空の城ラピュタ』の一度だけ。霜重の参考文献がテレビの感想文だった場面で、ずんだもんが強く突っ込む。他は質問・観察を中心にし、辛辣な反応を連打しない。林には独自の同語反復の考察を割り当てた。

モニターの大きさで変わる計測値、同じ映像3回の検証、門の追試、遺跡の年代推定も図解を維持。旧改修内容は `visual_audit_v5.md`。v5は途中稿であり、前回の完成動画はv4。

正体判明前はソバヤ／SOBAYA。大柄な体格・仮面の輪郭を黒いシルエットで示し、手ぶれ・遮蔽・ノイズ付きの証拠資料を使用。遺跡と門は適切な静止フレームを使い、別の顔やカットが混入しないようにした。鮮明な映像と「そば屋」「クローン」「ビール」は社員と判明してから解禁する。

研究者6名・所属6団体は架空。霜重の読みは「しもじゅう」。締めは「マドギワでの生息を希望される方」への高評価・登録案内。

## 再生成

VOICEVOX 0.25.1を `127.0.0.1:50021` で起動。

```sh
cd 03_SCRIPTS/youtube_sobaya_mystery_20261010/remotion
npm ci
../../../.local/voicevox-explainer/venv/bin/python prepare_assets.py
../../../.local/voicevox-explainer/venv/bin/python prepare_evidence.py
../../../.local/voicevox-explainer/venv/bin/python prepare_voice.py
npm run typecheck
npm run render
../../../.local/voicevox-explainer/venv/bin/python check_output.py
```

Remotion 4.0.534固定。前作からの立ち絵とローカルの原本動画を使用。画像生成は内蔵image_genによる参照付き生成。採用シルエットはGit管理の `inputs/sobaya_silhouette_v2.png` から復元できる。

音声はVOICEVOX:四国めたん／ずんだもん。採用設定は `production_record.json`。環境音楽は自作アンビエント、`mix_audio.py` で再現する。元動画の音声は再生せず、解説とBGMを配置する。

`public/`、`out/`、node_modules、生成動画はGit対象外。旧版の画面・音声はローカル保持、コードはGit履歴の `5138e2fa` から参照できる。

## 検証

全種類のレイアウトと証拠映像、正体判明前後の切替を実フレームで確認する。機械検査では116発話の存在、WAV実測尺、字幕長、時刻の整合、正体判明前の語彙、完成動画のフレーム数と終端までのデコードを確認。

音声の通し試聴は利用可能な手段がなく未実施。機械的な音声検査と区別する。結果は `qa_record.json` と `production_record.json`。
