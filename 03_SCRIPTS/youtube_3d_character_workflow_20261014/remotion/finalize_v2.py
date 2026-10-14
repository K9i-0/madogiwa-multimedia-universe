from pathlib import Path
import json,os,hashlib
P=Path(__file__).resolve().parent
rows=json.loads((P/'out/voice_progress_v2.json').read_text());expected=json.loads((P/'dialogue-v2.json').read_text());assert len(rows)==len(expected)
cursor=12
for d in rows:
 if not d.get('reuseAudio'):
  src=P/'public'/d['audio'];name=f"clip_v2_{d['id']}_{d['who']}{'_clear' if d['voiceSettings'].get('durationScale')==.85 else '_term' if d.get('take')=='term' else '_clarify' if d.get('take')=='clarify' else ''}.wav";dst=P.parent/name
  if not dst.exists():dst.write_bytes(src.read_bytes())
  assert hashlib.sha256(dst.read_bytes()).hexdigest()==d['audioSha256']
  link=P/'public'/name
  if not link.exists():link.symlink_to(os.path.relpath(dst,link.parent))
  d['audio']=name
 d['startFrame']=cursor;cursor+=d['durationInFrames']+d.get('pause',9)
end=cursor+42
m={'composition':{'width':1280,'height':720,'fps':30,'durationInFrames':end},'mainStartFrame':next(d['startFrame'] for d in rows if d['chapter'].startswith('2.')),'endingStartFrame':next(d['startFrame'] for d in rows if d['chapter'].startswith('8.')),'voiceModel':'Irodori Yametaro + VOICEVOX Chugoku Usagi','dialogue':rows,'clips':[],'creditsInDescription':True}
(P/'src/edit-manifest-v2.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(P.parent/'voice_record_v2.json').write_text(json.dumps({'subjectiveListening':False,'lines':[{k:v for k,v in d.items() if k!='envelope'} for d in rows]},ensure_ascii=False,indent=2))
header='''# Tripoで窓際族を3Dにする — 完成版v2\n\n2026-10-14の検討とv1視聴後の改修依頼を反映。完成例と到達点を先に見せ、実際の入力→Tripo→修正→動作→活用の順で進める。料金・契約・一般論は具体的な生成手順のあとへ移動。\n\n登場：やめ太郎（正典Irodori v4.1-Small、seed7）、たこさん（VOICEVOX中国うさぎ・ノーマル61、速度1.1・音高0）。新規・修復25発話、再利用66発話。v1は別ファイルとGit履歴に保持。\n\n冒頭のBlender版そば屋の制作担当は劇中設定。過去の回転動画・入力画像・モデル・修正資料は実素材を使用。そば屋は縦832×1108のWan動画から四方向を抽出。たこさんは前後2画像。福ギュンは実写人物の再現を調整した事例。\n\n料金は過去の制作記録に基づく2工程の例。Wan推定$0.56＋Tripo120 credits、1 credit=$0.01、1ドル160円で約282円。入力画像・再生成・開発エージェント等は含まない。StudioとAPIは別。\n\nAPI指示と端末の表示は、リポジトリの実装に沿った説明用の操作例。今回新たな有料生成を送信した映像とは扱わない。\n\n'''
script=header+f"タイムライン：{end/30:.3f}秒／1280×720／30fps。フレーム正本：`remotion/src/edit-manifest-v2.json`。\n\n";chapter=None
for d in rows:
 if d['chapter']!=chapter:chapter=d['chapter'];script+='\n## '+chapter+'\n\n'
 script+=f"- {d['id']} {'やめ太郎' if d['who']=='yametaro' else 'たこさん'}「{d['text']}」\n  - 画面：`{d['view']}`\n"
script+='\n## 制作資料\n\n- `asset_sources.json`／`voice_record_v2.json`／`review_v2.md`／`delivery_v2.json`\n- `tools/TRIPO.md`、`tools/tripo_multiview.py`\n- `.claude/skills/humanoid-motion/references/image-to-rigged-character.md`\n- 公式3D体験：https://madogiwa.work/characters/sobaya\n- Wan解説：https://www.youtube.com/watch?v=RMWefLVS9vQ\n- 料金・クレジット等の出典は`youtube_description.txt`。\n'
(P.parent/'script.md').write_text(script)
print('V2',end/30,'seconds',len(rows),'utterances')
