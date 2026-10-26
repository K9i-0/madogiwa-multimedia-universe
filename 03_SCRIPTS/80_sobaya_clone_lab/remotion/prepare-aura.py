from pathlib import Path
import json,subprocess,os
p=Path('03_SCRIPTS/80_sobaya_clone_lab'); r=p/'remotion'; a=r/'public/aura'; a.mkdir(exist_ok=True)
for src,dst in [(p/'final_remotion_clone_lab_skin.mp4',a/'source.mp4'),(r/'out/aura-prep/revenge.wav',a/'revenge.wav')]:
 if not dst.exists(): os.link(src,dst)
for name,x in [('yametaro',155),('fukuchan',1075)]:
 subprocess.run(['ffmpeg','-v','error','-ss',str(500/30),'-i',str(a/'source.mp4'),'-vf',f'crop=690:340:{x}:195','-frames:v','1','-y',str(a/f'{name}.png')],check=True)
for name,f in [('hold',753),('ending',829)]:
 subprocess.run(['ffmpeg','-v','error','-ss',str(f/30),'-i',str(a/'source.mp4'),'-frames:v','1','-y',str(a/f'{name}.jpg')],check=True)
segments=[{'id':'scan','from':0,'duration':192,'sourceStart':348,'sourceEnd':540,'rate':1},{'id':'hologram','from':192,'duration':214,'sourceStart':540,'sourceEnd':754,'rate':1},{'id':'hold','from':406,'duration':15,'sourceFrame':753},{'id':'break','from':421,'duration':105,'sourceStart':754,'sourceEnd':829,'rate':5/7},{'id':'escape','from':526,'duration':125,'sourceStart':829,'sourceEnd':954,'rate':1},{'id':'ending','from':651,'duration':30,'sourceFrame':829}]
caps=[]
for c in json.loads((p/'shorts-manifest-hologram.json').read_text())['captions']:
 for s in segments:
  if 'sourceStart' in s and s['sourceStart']<=c['startFrame']<s['sourceEnd']:
   caps.append({**c,'startFrame':s['from']+round((c['startFrame']-s['sourceStart'])/s['rate']),'endFrame':s['from']+round((min(c['endFrame'],s['sourceEnd'])-s['sourceStart'])/s['rate'])})
m={'composition':{'width':720,'height':1280,'fps':30,'durationInFrames':681},'segments':segments,'captions':caps,'music':{'url':'https://www.youtube.com/watch?v=mbSp4gsKaU0','title':'REVENGE (Super Slowed) — 1HXSX, wnorg17','startFrame':28,'impactOutputFrame':457,'analysis':'RMS rise / peak near source music 16.16s; music starts at 28/30s; main glass frame 780 at output457','beatFrames':[457,474,488,504,519,533,548,562,577,592,606,623,634,650,667]},'audioSource':'final_remotion_shorts_usagi_hologram_9x16.mp4','outputs':['final_remotion_aura_original_audio_9x16.mp4','final_remotion_aura_bgm_only_9x16.mp4']}
(r/'src/aura-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
