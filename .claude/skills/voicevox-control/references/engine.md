# エンジン・クエリ・再生成

2026-10-19時点でこの環境の `http://127.0.0.1:50021/version` は0.25.1。実際の稼働版を確認して使う。未起動なら既存の起動手順・実行ファイルを探す（この環境の例：`~/Applications/voicevox_engine/macos-arm64/run`）。同じポートへ重複起動しない。

APIの正本は稼働エンジンの `/docs` / `/openapi.json`。[公式API資料](https://voicevox.github.io/voicevox_engine/api/) と [公式READMEの音声合成例](https://github.com/VOICEVOX/voicevox_engine/blob/master/README.md) も参照する。将来の版でパラメータや配役が変わる可能性があるため、IDを名前から推測しない。

## 生成の順序

1. `GET /version` と `GET /speakers` で版とスタイルIDを確認する。`speaker` パラメータはスタイルIDで、話者UUIDとは別。
2. `POST /audio_query?text=...&speaker=...` に、辞書適用後の `speech` をURLエンコードして渡す。日本語を手作業でURLへ連結しない。
3. `kana` と `accent_phrases` のモーラを見て、意図した語の読みを確認する。
4. 採用済みの `speedScale`、`pitchScale`、`intonationScale`、`volumeScale`、`prePhonemeLength`、`postPhonemeLength`、サンプルレート等を設定する。
5. `POST /synthesis?speaker=...` へ最終AudioQueryをJSONで渡す。HTTP成功、WAVヘッダー、尺、無音・ピーク、修正語の発音を確認する。タイムアウト・APIエラーを空のWAVや成功済みキャッシュとして保存しない。

このリポジトリで一律の話速は決めない。配役の正本は [VOICE_CAST.md](../../../../02_CHARACTERS/VOICE_CAST.md)、作品の指定があればそれを優先する。廃村Y村の青山龍星・標準速度も作品固有の選択。速度調整には原則クエリの `speedScale` を使い、生成後の速度加工は明示的な演出がある場合に限る。

## 読みとアクセントを直す

**`AudioQuery.kana` は読み取り専用で、音声合成用クエリとしては無視される。** 0.25.1のOpenAPIでもこの旨を確認済み。かな文字列だけを書き換えて同じ `accent_phrases` を合成しても読み修正にならない。

- 誤読：音声用テキストを直し、`/audio_query` を再取得する。通常はこれが最小の修正。
- アクセントまで明示：`POST /accent_phrases` に `text`、`speaker`、`is_kana=true` を指定し、戻った配列をクエリの **`accent_phrases`** へ設定して合成する。
- 既存のアクセント句やモーラを直接変更：必要に応じ `POST /mora_data?speaker=...` に変更後のアクセント句配列を渡し、音高・長さを再計算する。返った配列と実際に合成した最終クエリを保存する。

`is_kana=true` は通常のカタカナ指定ではなく、AquesTalk風記法。句の区切りは `/` または `、`、アクセント位置は `'`、疑問は句末の `？` 等を使う。記法と例は [公式README](https://github.com/VOICEVOX/voicevox_engine/blob/master/README.md) と稼働版APIで確認する。誤読修正だけならこの記法を無理に導入しない。

## キャッシュと引き渡し

再生成を識別する情報：

- スタイルID、エンジン版、使用core版（APIが返す場合）と、合成時の追加オプション。
- 実際に合成した最終AudioQuery全体。`accent_phrases` と設定を含む正規化JSONからhashを作る。
- 原文、最終 `speech`、共有／作品辞書のhash・適用記録、最終WAVと実測尺。

辞書hashは由来の記録にも使う。無関係な語の追加だけで全音声を再生成する必要はないが、辞書を適用して最終クエリを確認する前に原文だけのキャッシュで打ち切らない。手修正したアクセント句をキャッシュキーから漏らさない。

変更行を生成し、WAV尺と映像の発話開始・終了、字幕、BGM・効果音のタイミングを [remotion-video](../../remotion-video/SKILL.md) へ渡す。音声・設定・辞書の検証と、最終ミックスでの聴感は別に記録する。

## エンジン常設のユーザー辞書を編集する場合

共有JSONの自動置換は作品内で完結し、エンジン常設辞書を変更しない。常設辞書の追加・編集を依頼された場合は以下を使う。

1. `GET /user_dict` で現在の語を読み、更新前のJSONを保存する。既存の同じ語の有無と設定を確認する。
2. 安定した固有名詞等だけを選び、読みはカタカナ、アクセント型・品詞・優先度は文中で確認して決める。すべてを `accent_type=0` にしない。文脈依存の `人`、`方`、`空` を常設辞書で強制しない。
3. 追加は `POST /user_dict_word`、更新は `PUT /user_dict_word/{word_uuid}`。稼働版では必須が `surface`、`pronunciation`、`accent_type`、任意が `word_type`、`priority`。返ったUUIDと設定を記録する。
4. 対象語を含む文と別の意味の文を `/audio_query` で検証する。不要な一括インポートや他作品の既存語の削除はしない。

常設辞書は同じエンジンを使う他作品にも影響する。編集後の確認と復元に必要なUUID・旧値を保持する。[公式のユーザー辞書API](https://github.com/VOICEVOX/voicevox_engine/blob/master/README.md) を参照する。
