# 窓貴族 v11 音声比較（2026-10-06）

ユーザー依頼：福ギュンの生成時の発話を基準に普段の声とリップシンクを改善し、たこさんを指定元リポジトリの方式で試す。採用済みv10と正典VOICE_CASTは保持。v11は試聴・比較用。最終的な声質の採用判断は未実施。

## 比較内容

- `final_remotion_subtitles_v11_seedvc.mp4`：福ギュンは元動画の発話からSeed-VCで声質変換。正典`02_CHARACTERS/Fukuchan_voice.wav`を声質の参照に使用。元の発話間隔を保つための候補。
- `final_remotion_subtitles_v11_irodori.mp4`：福ギュンはIrodori v4-Largeで正典声を参照して再合成。先頭だけを元音声に合わせた比較候補。元の内部ポーズ・音素時刻は引き継がない。リップシンク改善済みとは扱わない。
- 両方のたこさん：VOICEVOX 0.25.1、Voidoll（ノーマル89）、speedScale=1.0。他パラメーターはaudio_query既定値。生成テキスト「本番もお燃えになってますわ。」。クエリの読みは「ホンバンモ／オモエニ／ナッテマスワ」。
- そば屋・やめ太郎、6回の通知、BGM、場面間の間、字幕、映像タイミングは保持。末尾2秒カードへ`VOICEVOX:Voidoll(CV:丹下桜)`を追記。1162フレーム、30fps、1280×720、38.733秒。

## 指定リポジトリの確認

[VOICE_CAST.md](https://github.com/sobaya-0141/Seedance_Madogiwa/blob/af92df24b277a45450cda975b0549d4c6ee890e4/02_CHARACTERS/VOICE_CAST.md)と`.claude/skills/seedance/voicevox_speak.sh`を個別取得。全体同期はしていない。元のたこさんはIrodoriではなくVOICEVOX/Voidoll。今回の候補だけに適用し、MMU全体の配役は変更しない。

個人利用の指定クレジットを[VOICEVOX公式の音声モデル規約](https://github.com/VOICEVOX/voicevox_vvm/blob/main/TERMS.txt)で確認し、エンドカードに記載。

## 入力と生成の再現

リポジトリルートで実行。中間・候補WAVは`.local/mado-kizoku-voice-v11/`、公開ディレクトリの派生音声は`remotion/public/voice-v11/`に保持しGit追跡しない。

```sh
mkdir -p .local/mado-kizoku-voice-v11/upstream
curl -fL https://raw.githubusercontent.com/sobaya-0141/Seedance_Madogiwa/af92df24b277a45450cda975b0549d4c6ee890e4/.claude/skills/seedance/voicevox_speak.sh -o .local/mado-kizoku-voice-v11/upstream/voicevox_speak.sh
VOICEVOX_ENGINE_DIR="$HOME/Applications/voicevox_engine/macos-arm64" bash .local/mado-kizoku-voice-v11/upstream/voicevox_speak.sh '本番もお燃えになってますわ。' .local/mado-kizoku-voice-v11/takosan_voidoll.wav 89 1.0
ffmpeg -y -i 03_SCRIPTS/87_mado_kizoku/wan3_fukuchan_closeup_480p.mp4 -vn -ac 1 -ar 24000 .local/mado-kizoku-voice-v11/fukugyun_original.wav
ffmpeg -y -i .local/mado-kizoku-voice-v11/fukugyun_original.wav -t 3.467 .local/mado-kizoku-voice-v11/fukugyun_source_trim.wav
IRODORI_TTS_CHECKPOINT=Aratako/Irodori-TTS-v4-Large IRODORI_CFG_SCALE_TEXT=5 IRODORI_UNCUT=1 IRODORI_DURATION_SCALE=0.7 tools/irodori_speak.sh 'こちらのお菓子も、ギュンですわ。' .local/mado-kizoku-voice-v11/fukugyun_irodori_large.wav 02_CHARACTERS/Fukuchan_voice.wav 100
```

Seed-VCは既設`.local/seed-vc`（MPS float32/F0・CPU BigVGAN修正済み）。以下は別シェルで実行：

```sh
repo_root="$PWD"
cd .local/seed-vc
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python inference.py --source "$repo_root/.local/mado-kizoku-voice-v11/fukugyun_source_trim.wav" --target "$repo_root/02_CHARACTERS/Fukuchan_voice.wav" --output "$repo_root/.local/mado-kizoku-voice-v11/seedvc" --diffusion-steps 50 --length-adjust 1.0 --inference-cfg-rate 0.7 --f0-condition True --auto-f0-adjust True --semi-tone-shift 0 --fp16 False
```

Seed-VC raw出力は3.448秒。104フレームへ無音を補い、元動画の無発話部に生じた変換ノイズだけを15msフェード付きで抑制。時間伸縮・映像の速度変更は不使用。元の発話区間1.089–2.088秒と2.608–3.341秒を基準にした。完全な音素同期は保証しない。

```sh
.local/Irodori-TTS/.venv/bin/python 03_SCRIPTS/87_mado_kizoku/remotion/prepare_voice_comparison.py
cd 03_SCRIPTS/87_mado_kizoku/remotion
npm run typecheck
npm run render:voice-seedvc
npm run render:voice-irodori
```

## 確認と制限

機械記録：`../voice_comparison_v11_record.json`。2区間以外の音声PCM一致、ピーク、動画デコード、字幕/クレジット画像を確認。福ギュンの元音声・Irodori・Seed-VCはWhisper-smallで全文認識。VOICEVOXは音素クエリの読みを確認（Whisperは「本端も思いになってますわ」と誤表記するためASR一致とは扱わない）。

この環境では音声の直接試聴ができない。声質・自然さ・細かな口パクはユーザーの試聴待ち。Seed-VCのローダーは既存環境と同じshape mismatchのスキップ警告を出した。ログを`.local/mado-kizoku-voice-v11/seedvc.log`に保持し、警告を合格扱いで隠さない。

Irodoriで句を分けた追加試作も行ったが、元の短い発声より長くなったため不使用。候補ファイルは`.local`にのみ保持。無理な時間圧縮で合わせてはいない。
