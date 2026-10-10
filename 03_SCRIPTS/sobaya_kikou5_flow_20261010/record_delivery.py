from pathlib import Path
import json,hashlib,subprocess
p=Path(__file__).resolve().parent;root=p.parents[1];m=json.loads((p/'remotion/src/edit-manifest.json').read_text());rows=m['dialogue']
record=[]
for r in rows:
 d={k:v for k,v in r.items() if k not in ['envelope','caption']};d['seconds']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p/r['audio'])]));record.append(d)
(p/'voice_record.json').write_text(json.dumps({'engine':'VOICEVOX 0.25.1 / Irodori v4.1 Small','referenceSha256':hashlib.sha256((root/'02_CHARACTERS/Yametaro_voice.wav').read_bytes()).hexdigest(),'listening':'Not independently performed; automated ASR and VOICEVOX kana checked separately','lines':record},ensure_ascii=False,indent=2))
titles={'intro':'自己紹介・そば屋とは','excel':'Excelを開いて、閉じて','catch':'ビールだけを救う超反応','bar':'ベランダをバーに改装','quake':'ビール禁止でオフィスが揺れる','proxy':'仮面をかぶせて代理出社','ending':'まとめ'}
seen=set();chapters=[]
for r in rows:
 if r['scene'] in seen:continue
 seen.add(r['scene']);f=r['startFrame']
 if r['scene']=='proxy':f=next(c['startFrame'] for c in m['clips'] if c['id']=='proxy')
 t=0 if r['scene']=='intro' else f//30;chapters.append(f'{t//60}:{t%60:02} {titles[r["scene"]]}')
(p/'youtube_description.txt').write_text('そば屋の奇行5選｜たこさん＆やめ太郎\n窓際族物語の過去エピソードを振り返ります。\n\n'+'\n'.join(chapters)+'\n\n声：VOICEVOX:Voidoll（たこさん）、Irodori-TTS（やめ太郎）\n立ち絵・キャラクター：窓際族物語\n引用：動画第59話・第34話・第48話（Prime版）・第76話（修正版2）・第53話\n\nBGM：昼下がり気分／KK\nhttps://opentracks.com/bgm/detail/4695\nBGM：ほのぼのワルツ【リコーダー】／エクシエ\nhttps://commons.nicovideo.jp/works/nc116360\nMusic: TheFatRat - Unity\nWatch the official music video: https://www.youtube.com/watch?v=n8X9_MgEdCg\n')
print('\n'.join(chapters));print('Total',m['composition']['durationInFrames']/30)
