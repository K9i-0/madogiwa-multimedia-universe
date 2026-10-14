from pathlib import Path
import json,os,hashlib,subprocess,sys
P=Path(__file__).resolve().parent
rows=json.loads((P/'out/voice_progress.json').read_text());expected=json.loads((P/'dialogue.json').read_text());assert len(rows)==len(expected),(len(rows),len(expected))
omit=set(json.loads((P/'edit_selection.json').read_text())['omit']);rows=[d for d in rows if d['id'] not in omit];cursor=60
for d in rows:
 src=P/'public'/d['audio'];name=f"clip{d['id'][1:]}_line1_{d['who']}{'_term_clear' if d.get('take')=='term_clear' else ''}.wav";dst=P.parent/name
 if not dst.exists():dst.write_bytes(src.read_bytes())
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==d['audioSha256']
 target=P/'public'/name
 if not target.exists():target.symlink_to(os.path.relpath(dst,target.parent))
 d['audio']=name;d['startFrame']=cursor;cursor+=d['durationInFrames']+d.get('pause',12)
end=cursor+75
m={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':end},'mainStartFrame':next(d['startFrame'] for d in rows if d['chapter'].startswith('3.')),'endingStartFrame':next(d['startFrame'] for d in rows if d['chapter'].startswith('10.')),'voiceModel':'Irodori Yametaro + VOICEVOX Chugoku Usagi','dialogue':rows,'clips':[],'creditsInDescription':True}
(P/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(P/'prepare_timing.py')],check=True)
(P.parent/'voice_record_v1.json').write_text(json.dumps({'subjectiveListening':False,'lines':[{k:v for k,v in d.items() if k!='envelope'} for d in rows]},ensure_ascii=False,indent=2))
script='''# Tripoで窓際族を3Dにする — 初稿v1\n\n2026-10-14制作。たこさん（VOICEVOX中国うさぎ・ノーマル61、速度1.1、音高0）＆やめ太郎（Irodori v4.1-Small、正典参照、seed7、本文CFG5、生成尺倍率0.70（Codex読み修復の2発話は0.85）、トリムなし）。\n\nユーザーとの台本検討を統合。冒頭のBlender版そば屋は第44話用の既存画像を利用し、「やめ太郎がCodexで作った」は劇中設定。そば屋の採用工程は縦832×1108・約8秒のWan動画から四方向を抽出した実例。たこさんは前後2画像の別経路。福ギュンは実写人物の再現で苦労した事例として短く紹介する。\n\n追加支払いだけでなく制作時間を含めたコストの話は、本作の制作上の判断であり、汎用モデル全般の性能評価ではない。TripoのStudioとAPIは別契約。価格は1ドル160円の固定換算で、過去の回転動画推定$0.56＋Tripo実消費120 creditsを約282円と説明。入力画像・再生成・Codex等の利用料は別。\n\n映像：採用済みExcel風画面、正典立ち絵、Three.jsで採用GLBをフレーム時刻から描画。公式サイトの実操作録画、AR入口の実画面、Flutter Sceneゲームの保存済みスクリーンショットを紹介。ARの実機撮影を行ったとは扱わない。\n\n'''+f"完成タイムライン：{end/30:.3f}秒／1280×720／30fps。発話・字幕・映像のフレーム正本は`remotion/src/edit-manifest.json`。\n\n"
chapter=None
for d in rows:
 if d['chapter']!=chapter:chapter=d['chapter'];script+='## '+chapter+'\n\n'
 script+=f"- {d['id']} {'やめ太郎' if d['who']=='yametaro' else 'たこさん'}「{d['text']}」\n  - 中央資料：`{d['view']}`\n"
script+='''\n## 正本・再現\n\n- セリフ候補全体：`remotion/dialogue.json`。採用から外した重複部分：`remotion/edit_selection.json`。\n- 音声の生成設定とハッシュ：`voice_record_v1.json`。候補はGit管理せず、採用WAVを本ディレクトリ直下に保存。\n- 入力素材とハッシュ：`asset_sources.json`。共有モデルは相対symlink参照。\n- たこさん：`04_GAME_ASSETS/3d/characters/takosan/rig_radial_v6_lined/`。\n- そば屋：`04_GAME_ASSETS/3d/characters/sobaya/motion_v3_20260917/`。\n- 福ギュン：`04_GAME_ASSETS/3d/characters/fukuchan/web_v3_20260917/`。\n- 浮遊：`tools/takosan_float_motion.mjs`の採用E/curlを固定速度で直接時刻評価。新規リグ・新規キャラクターモーションは制作しない。\n- Tripo接続：`tools/TRIPO.md`、複数画像：`tools/tripo_multiview.py`。\n- 料金・利用案内： https://www.tripo3d.ai/pricing / https://developers.tripo3d.ai/en/pricing / https://developers.tripo3d.ai/en\n- 公式サイト： https://madogiwa.work/characters/sobaya\n- 公開済みWan解説： https://www.youtube.com/watch?v=RMWefLVS9vQ\n- 完成版の確認範囲と制約：`review_v1.md`。クレジット・リンクは`youtube_description.txt`。\n'''
(P.parent/'script.md').write_text(script)
print('ADOPTED',len(rows),'lines',end/30,'seconds')
