from pathlib import Path
import json,subprocess,shutil,wave,hashlib
import numpy as np
r=Path(__file__).resolve().parent;ep=r.parent;root=ep.parent.parent;bank=root/'.local/yumemi_evolution_20261026/sfx';pub=r/'public/sfx_variants';pub.mkdir(exist_ok=True);out=r/'out';out.mkdir(exist_ok=True)
m=json.loads((r/'src/solo-manifest.json').read_text());n=m['durationInFrames']*1600
lookup={f.stem:f for pack in ['interface','music-jingles','digital-audio'] for f in (bank/pack).rglob('*.ogg')}
lookup['applause']=root/'03_SCRIPTS/75_madogiwa_tshirt_keynote/audio_sources/applause_cc0.ogg';lookup['laughter']=root/'03_SCRIPTS/75_madogiwa_tshirt_keynote/audio_sources/laughter_ccby4.mp3'
def decode(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ac','2','-ar','48000','-']),dtype='<f4').reshape(-1,2).copy()
voice=decode(ep/'final_remotion_yumemin_only.mp4')[:n];cache={};sources={}
def asset(name):
 if name in cache:return cache[name]
 src=lookup[name];dst=pub/(name+'.wav')
 if dst.exists():d=decode(dst)
 else:
  d=decode(src)
  if name in ['applause','laughter']:d=d[int(.3*48000):int(2.5*48000)]
  active=np.where(np.max(np.abs(d),axis=1)>.002)[0]
  if len(active):d=d[max(0,active[0]-240):min(len(d),active[-1]+2400)]
  fade=min(2400,len(d)//5);d[-fade:]*=np.linspace(1,0,fade)[:,None];d[:min(240,len(d))]*=np.linspace(0,1,min(240,len(d)))[:,None]
  with wave.open(str(dst),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes((np.clip(d,-1,1)*32767).astype('<i2').tobytes())
 sources[name]={'sourceFile':str(src.relative_to(root)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()};cache[name]=d;return d
# Exact source-video event frames converted to the edited 20.133 s timeline.
variants={
 'keynote':[(2,'jingles_STEEL00',-15),(46,'maximize_007',-15),(77,'glass_001',-15),(104,'confirmation_002',-12),(112,'applause',-17),(153,'maximize_007',-14),(188,'glass_002',-17),(202,'glass_003',-16),(218,'glass_004',-15),(249,'jingles_STEEL02',-14),(282,'confirmation_001',-15),(319,'applause',-16),(369,'maximize_009',-12),(393,'jingles_STEEL00',-12),(415,'applause',-14)],
 'comedy':[(2,'jingles_PIZZI00',-13),(46,'bong_001',-13),(77,'scratch_001',-14),(104,'jingles_SAX00',-12),(120,'laughter',-15),(153,'drop_004',-12),(188,'pluck_001',-13),(202,'pluck_002',-13),(218,'bong_001',-12),(249,'jingles_PIZZI02',-13),(282,'drop_002',-13),(301,'drop_003',-13),(319,'jingles_SAX03',-12),(329,'laughter',-15),(369,'scratch_003',-13),(393,'bong_001',-11),(423,'laughter',-12)],
 'intense':[(0,'jingles_HIT00',-11),(43,'phaserUp1',-12),(49,'jingles_HIT02',-11),(78,'laser1',-13),(102,'powerUp1',-12),(112,'jingles_HIT03',-12),(151,'phaserUp3',-12),(159,'jingles_HIT00',-11),(188,'laser2',-14),(202,'laser3',-13),(218,'powerUp3',-12),(247,'phaseJump1',-11),(253,'jingles_HIT02',-11),(280,'laser4',-13),(295,'laser6',-13),(310,'powerUp7',-12),(325,'jingles_HIT03',-12),(366,'phaserUp1',-11),(377,'jingles_HIT00',-11),(393,'powerUp1',-11),(413,'jingles_HIT02',-10)]}
reports=[]
for name,cues in variants.items():
 track=np.zeros((n,2),np.float32);events=[]
 for sf,sample,db in cues:
  sc=next(s for s in m['scenes'] if s['sourceStartFrame']<=sf<s['sourceEndFrame']);frame=round(sc['startFrame']+(sf-sc['sourceStartFrame'])/sc['playbackRate']);d=asset(sample);gain=10**(db/20)/max(float(np.max(np.abs(d))),1e-5);start=frame*1600;count=min(len(d),n-start);piece=d[:count].copy()
  # End sounds gracefully at the existing video boundary.
  if count<len(d):fade=min(7200,count);piece[-fade:]*=np.linspace(1,0,fade)[:,None]
  track[start:start+count]+=piece*gain
  events.append(dict(startFrame=frame,file='sfx_variants/'+sample+'.wav',volume=gain,durationInFrames=int(np.ceil(count/1600)),sourceVideoFrame=sf,targetPeakDbfs=db))
 scale=1.
 while np.max(np.abs(voice+track*scale))>.89:scale*=.95
 mix=voice+track*scale;wav=out/f'variant_{name}.wav'
 with wave.open(str(wav),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes((mix*32767).astype('<i2').tobytes())
 for e in events:e['volume']*=scale
 (r/f'src/sound-{name}-manifest.json').write_text(json.dumps(dict(durationInFrames=m['durationInFrames'],events=events),ensure_ascii=False,indent=2)+'\n')
 dest=ep/f'final_remotion_yumemin_{name}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(ep/'final_remotion_yumemin_only.mp4'),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t',str(n/48000),'-movflags','+faststart',str(dest)],check=True)
 reports.append(dict(name=name,cues=len(cues),effectGain=scale,peakDbfs=float(20*np.log10(np.max(np.abs(mix)))),output=dest.name));print(reports[-1],flush=True)
(ep/'sound-variants-audit.json').write_text(json.dumps(dict(variants=reports,sources=sources,listenStatus='not_auditioned'),ensure_ascii=False,indent=2)+'\n')
for pack in ['interface','music-jingles','digital-audio']:shutil.copy2(bank/pack/'License.txt',pub/(pack+'-License.txt'))
