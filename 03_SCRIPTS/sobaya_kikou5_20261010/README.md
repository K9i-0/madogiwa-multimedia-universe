# そば屋の奇行5選

完成動画：`final_remotion_kikou5.mp4`（1280×720／30fps／5399フレーム・約3分）。`preview.html`から再生可能。

ユーザー採用台本の解説動画。たこさんは淡々と、ときどき辛辣。やめ太郎は辛辣なツッコミと、たこさんへの制止を担当。人物紹介→ベランダ居酒屋→やめさん確保キャンペーン→ビール電池→タクシー→禁酒地震→締め。

## 再現

1. VOICEVOX Engineを127.0.0.1:50021で起動（制作時0.25.1）。
2. `python3 generate_voice.py`。たこさん＝Voidoll ノーマル89／speed1。やめ太郎＝Irodori-TTS v4.1-Small／正典Yametaro_voice.wav／seed7／caption空／CFG5／uncut／尺倍率はdialogue.json。
3. `python3 prepare_assets.py`。既存原作・動画・BGM・共有立ち絵から編集用素材を準備。素材出典・フレームはassets.json。
4. Irodori環境のPythonで`remotion/prepare.py`と`remotion/mix_audio.py`。新規音声を-18LUFS、原音クリップを-19LUFS、本編BGMを-34LUFS、Unityを-38LUFSへ。原音クリップ中はBGMを0.08倍にダッキング。末尾の音量持ち上げなし。
5. remotionで`npm ci`、`npm run typecheck`、`npm run render`。
6. `python3 verify.py`。完成720p・30fps・フレーム数・全編デコード・画面抽出を確認。

台本はdialogue.json、タイミング正本はremotion/src/edit-manifest.json。過去クリップは解説と重ねず原音付きで再生。第76話はやめ太郎が注ぐ修正版2を引用し、後発のとーくん版とは区別。新規映像生成なし。元動画、他作品、全体ボイス正典は維持。

## BGM

アーロンチュア解説の採用ファイルと同一ハッシュの素材を使用。
- 昼下がり気分／KK：https://opentracks.com/bgm/detail/4695
- ほのぼのワルツ【リコーダー】／エクシエ：https://commons.nicovideo.jp/works/nc116360
- TheFatRat - Unity：https://www.thefatrat.com/release/unity
- Unity公式利用条件：https://www.thefatrat.com/terms-and-conditions と https://www.thefatrat.com/copyright を2026-10-10再確認。YouTube解説向けクレジットはyoutube_description.txt。公開操作は未実施。

## 確認範囲

ASRは文章照合の補助であり、声の自然さ・演技・精密な口パク同期の聴覚確認ではない。独立した通し試聴は未実施。
