# 読み辞書の運用

[readings.json](readings.json) が共有正本。過去の誤読修正と採用済みの読みを集めたもので、全エントリーを全話者で試聴済みという意味ではない。出典はファイル内の `sources` を参照する。

## 使い分け

| 仕組み | 用途 |
|---|---|
| `replacements` | 読みを固定できる単語・十分に狭い語句を音声用テキストで置換する |
| `context_checks` | 自動置換せず、前後とAudioQueryを確認する候補を出す |
| `speech_override` | 特定の行の読みを全文で明示する。共有・ローカル置換とも適用せず、そのまま使う |
| `--local-dictionary` | 作品内だけの用語・採用読み。共有辞書に加えて使う |

`common` は常に有効。`mmu` は人物・作品名、`tech` は技術語、`y-village` は廃村Y村の略称と儀式用語。必要なものを `--scope mmu --scope y-village` のように選ぶ。未知のscopeはエラーにする。

表示の `text` と音声用の `speech` は別に保持する。`text` をかなへ書き換えない。既存の明示読みは `speech_override` に移し、作品固有の読みを優先する。途中まで直した文字列を `speech_override` として渡すと残りの自動補正も止まるため、行全体を確認する。

## ファイル形式

共有・ローカルとも `schema_version: 1`。主なフィールド：

- `scopes`: scope名→説明。ローカルでは追加したscopeだけ宣言してよい。
- `sources`: 出典ID→説明・リポジトリ内の記録パス。
- `replacements`: `id`、`surface`、`reading`、`scope`（省略時common）、`match`（省略時literal）、`source`、`note`。
- `context_checks`: `id`、`surface`、`readings`（判断例の配列）、`note`、`source`。同様にscopeを指定できる。

`match: literal` は大文字小文字を区別する文字列一致。`ascii_token` はASCII英数字・アンダースコアに接する略語の部分一致も避ける（`IT` を `GITHUB` の中で置換しない）。形態素解析や日本語の単語境界を保証するものではない。広すぎる断片は登録しない。

`kanji_word` は前後に漢字（CJK基本・拡張A・互換漢字・々）が接する場合を除外する。単独の `祠` を補正しても `祠堂` はそのまま残す。必要な複合語が対象外になった場合は語句単位で登録する。

処理は原文を一度だけ走査し、左端の一致から採用する。同じ位置ではローカル辞書を優先し、その中で最長の語句を採用する。置換後の文字列へ再び辞書を掛けない。ローカルで共有と同じ `id` を定義すると、そのエントリーを置き換える。

ローカル辞書の最小例：

```json
{
  "schema_version": 1,
  "replacements": [
    {
      "id": "episode.project-a",
      "surface": "A計画",
      "reading": "エー計画",
      "source": "script.md の採用台詞",
      "note": "この作品のプロジェクト名"
    }
  ]
}
```

字幕行の例：

```json
[
  {"id": "line-01", "text": "管理人が空の缶を拾った。"},
  {
    "id": "line-02",
    "text": "こちらに来る方です。",
    "speech_override": "こちらに来るカタです。"
  }
]
```

## 既存の生成処理へ組み込む

CLIの出力JSONを読むか、作品スクリプトから同じヘルパーを呼ぶ。`repo_root` はその作品で求めたリポジトリルートを渡す。共有コードを作品へコピーしない。

```python
import sys
sys.path.insert(0, str(repo_root / ".claude/skills/voicevox-control/scripts"))
from prepare_readings import load_dictionary, prepare_row

dictionary = load_dictionary()  # 必要なら local_path=... を指定
# VOICEVOXの行だけを取り出して処理する。
voice_row = dict(row)
# 既存作品の明示読みを移す。新規のspeech_overrideを最優先する。
if "speech_override" not in voice_row:
    for field in ("voicevoxReading", "reading"):
        if voice_row.get(field):
            voice_row["speech_override"] = voice_row[field]
            break
prepared = prepare_row(voice_row, dictionary, scopes=["mmu", "tech"])
# /audio_query の text パラメータには prepared["speech"] を渡す。
# 字幕には元の row["text"] を使う。
```

出力の `reading_report` には `method`（dictionary / explicit）、`applied`、`review`、有効scope、辞書のSHA-256を保存する。`start` / `end` は元の `text` のPython文字位置（0始まり、末尾を含まない）。確認候補は誤読の断定ではない。既知の語句で補正した範囲は候補から除外し、明示読みの行は全文指定済みとして候補を返さない。元の `speech_override` 自体の誤読・脱落は生成後に確認する。

同じ文字でも違う読みになるため、確認候補を一律に片方へ寄せない：

- `空の缶` → から。`空の色` → そら。`空き缶` → あきかん。`空席` → くうせき。
- `こちらへ来る方` → 人ならかた。`明日来る方がいい` → 比較ならほう。
- `あの人` → ひと。`三人` → さんにん。`日本人` → にほんじん。
- `客の杯` → 儀式の器ならさかずき。`一杯` / `乾杯` は別。
- `通って` → 道をとおって／学校にかよって。
- `その間` → 時間ならあいだ。`間を置く` → ま。

クエリのモーラ表記は `ホオ` / `トオ` のように長音を母音で返すことがある。表記の差だけで誤読と判定しない。`日本人` のにほんじん／にっぽんじん等、採用方針で限定していない許容読みも区別する。

## 追加・改修の手順

1. 誤読した行、実際の読み、意図する読み、話者・エンジン、修正結果を作品の記録へ残す。
2. 共通化できる範囲を選ぶ。単語に切り出すと多義になる場合は、語句を長くするか文脈確認へ回す。数字を一桁ずつ読むパスワード等は行指定を使う。
3. `source` と `note` を付け、再発防止に必要なエントリーだけ追加する。誤読した漢字をすべてカナへする巨大置換表にしない。
4. 元の例、別の意味の例、助数詞・複合語を確認し、該当箇所のクエリを作り直す。読み・アクセントが自然なら採用する。
5. 新しい語を辞書へ足しただけで過去動画を再生成しない。生成依頼または対象行の修正時に適用する。
