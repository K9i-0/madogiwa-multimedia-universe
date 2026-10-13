"""Preserve adopted narration inputs and refresh delivery-facing documentation."""
from pathlib import Path
import json,hashlib,os
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());items=[]
for d in m['dialogue']:
 src=P/'public'/d['audio'];dst=P.parent/f'v5_{d["id"]}_{d["who"]}.wav'
 if d['audio'].startswith('duo_'):
  previous=json.loads((P.parent/'duo_adopted_audio.json').read_text())['audio']
  match=next(x for x in previous if x['publicAudio']==d['audio'])
  dst=P.parent/match['file']
 digest=hashlib.sha256(src.read_bytes()).hexdigest()
 if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
 else:os.link(src,dst)
 items.append({'id':d['id'],'file':dst.name,'publicAudio':d['audio'],'sha256':digest,'who':d['who']})
(P.parent/'adopted_audio_v5.json').write_text(json.dumps({'version':5,'audio':items},ensure_ascii=False,indent=2)+'\n')
chapters=[]
for d in m['dialogue']:
 if not any(c['chapter']==d['chapter'] for c in chapters):
  secs=0 if not chapters else d['startFrame']//30
  chapters.append({'chapter':d['chapter'],'startFrame':0 if not chapters else d['startFrame'],'youtubeTime':f'{secs//60:02}:{secs%60:02}'})
sources=json.loads((P.parent/'sources.json').read_text());sources.update(version=5,chapters=chapters)
sources['narration']['takosan']['pitchScale']=0
sources['narration']['yametaro']='Irodori-TTS v4.1-Small; canonical reference, new dialogue and unchanged adopted lines'
sources['narration']['record']='voice_record_v5.json';sources['narration']['scope']='たこさんは2026-10-13採用の共通VOICEVOX設定。作品別に無音長を調整。'
sources['delivery']={'file':'final_remotion_ai_video_workflow_v5.mp4','width':1280,'height':720,'fps':30,'durationInFrames':m['composition']['durationInFrames'],'durationSeconds':m['composition']['durationInFrames']/30,'newPaidVideoGeneration':False,'published':False,'previousVersionPreserved':['final_remotion_ai_video_workflow_v4.mp4']}
sources['scenarioReferences']=['https://qiita.com/Yametaro/items/a40ffcd65d77ed8b29a0','https://qiita.com/Yametaro/items/21b8772e6c0d1d77e176','https://qiita.com/Yametaro/items/255eea3124e769ce845c']
for e in sources['examples']:
 if e['episode'] in (85,69):e['usage']='v4以前の導入作例。v5ではこの動画クリップを使用しない。'
(P.parent/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
p=P.parent/'youtube_description.txt';s=p.read_text();a=s.index('チャプター\n');b=s.index('\n制作リポジトリ',a)
s=s[:a]+'チャプター\n'+'\n'.join(c['youtubeTime']+' '+c['chapter'] for c in chapters)+'\n'+s[b:]
s=s.replace('音高−0.04','音高0').replace('使用映像：窓際族物語 第85話「パクられた」、第53話','使用映像：窓際族物語 第53話').replace('、第69話「窓際スーパーつらい」、第72話','、第72話')
marker='本動画は、たこさんの声を' if '本動画は、たこさんの声を' in s else '台本構成の参考：'
s=s[:s.index(marker)]+'台本構成の参考：無職やめ太郎さんの会話形式の記事\n'+'\n'.join(sources['scenarioReferences'])+'\n\n導入と全編の掛け合いを改稿したv5。たこさんは中国うさぎ・ノーマルです。\n'
p.write_text(s)
lines=['# Codexで動画まで作る。窓際族物語のAI制作術 — v5','','対象：Codex / Claude Codeでサイト・アプリを作る人。導入は共感→作例→全容。全編は願望と困りごとから技術へ進む。','','配役：やめ太郎（Irodori v4.1-Small）、たこさん（VOICEVOX:中国うさぎ・ノーマル、速度1.1、音高0）。末尾クレジットなし。YouTube未公開。','','完成版：`final_remotion_ai_video_workflow_v5.mp4`。音声設定・ハッシュ：`voice_record_v5.json`。検査結果：`review_v5.md`、`delivery_v5.json`。','','参考（構成・会話の研究。セリフは今回のオリジナル）：']+['- '+u for u in sources['scenarioReferences']]
chapter=None
for r in m['dialogue']:
 if chapter!=r['chapter']:chapter=r['chapter'];lines+=['',f'## {chapter}','']
 sec=r['startFrame']//30
 lines.append(f"- `{r['id']}` {sec//60:02}:{sec%60:02} {'やめ太郎' if r['who']=='yametaro' else 'たこさん'}：{r['text']} （画面：{r['view']}）")
 for c in m['clips']:
  if c['afterId']==r['id']:lines.append(f"  - 作例：{c['label']}／{c['durationInFrames']/30:.1f}秒、原音・実況停止")
(P.parent/'script.md').write_text('\n'.join(lines)+'\n')
print('ADOPTED',len(items),m['composition']['durationInFrames']/30)
