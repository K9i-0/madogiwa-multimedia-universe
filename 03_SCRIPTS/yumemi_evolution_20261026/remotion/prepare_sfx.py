from pathlib import Path
import json,subprocess,shutil,hashlib,wave
import numpy as np
r=Path(__file__).resolve().parent;ep=r.parent;root=ep.parent.parent
source=root/'.local/yumemi_evolution_20261026/sfx/interface';assets=r/'public/sfx';assets.mkdir(exist_ok=True)
m=json.loads((r/'src/solo-manifest.json').read_text());n=m['durationInFrames']*1600
# source video frame, sample, peak dBFS, visual cue
cues=[(3,'pluck_001',-23,'タイトル'),(46,'open_002',-22,'大喜利へ切替'),(104,'pluck_002',-19,'いいね数登場'),(153,'open_002',-22,'ゆめプロへ切替'),(188,'pluck_001',-24,'活動項目1'),(202,'pluck_001',-24,'活動項目2'),(218,'pluck_002',-23,'活動項目3'),(249,'open_002',-22,'窓際族へ切替'),(282,'pluck_001',-23,'グッズ登場'),(301,'pluck_002',-22,'グッズ追加'),(319,'confirmation_001',-21,'実際に売れた'),(369,'open_002',-22,'進化全景へ切替'),(393,'confirmation_002',-19,'最後のコピー')]
def decode(path):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ac','2','-ar','48000','-']),dtype='<f4').reshape(-1,2).copy()
track=np.zeros((n,2),dtype=np.float32);events=[]
for sf,name,db,label in cues:
 src=source/'Audio'/f'{name}.ogg';dst=assets/src.name
 if not dst.exists():shutil.copy2(src,dst)
 scene=next(s for s in m['scenes'] if s['sourceStartFrame']<=sf<s['sourceEndFrame'])
 frame=round(scene['startFrame']+(sf-scene['sourceStartFrame'])/scene['playbackRate'])
 d=decode(dst);gain=10**(db/20)/max(float(np.max(np.abs(d))),.00001)
 start=frame*1600;end=min(n,start+len(d));track[start:end]+=d[:end-start]*gain
 events.append(dict(startFrame=frame,file='sfx/'+dst.name,volume=gain,durationInFrames=int(np.ceil(len(d)/1600)),label=label,sourceVideoFrame=sf,targetPeakDbfs=db))
voice=decode(ep/'final_remotion_yumemin_only.mp4');mix=track.copy();mix[:min(n,len(voice))]+=voice[:n]
peak=float(np.max(np.abs(mix)));assert peak<.99,peak
out=r/'out';out.mkdir(exist_ok=True);wav=out/'solo_sfx_mix.wav'
with wave.open(str(wav),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000);f.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
(r/'src/solo-sfx-manifest.json').write_text(json.dumps(dict(durationInFrames=m['durationInFrames'],events=events),ensure_ascii=False,indent=2)+'\n')
if (source/'License.txt').exists():shutil.copy2(source/'License.txt',assets/'License.txt')
record=dict(source='https://kenney.nl/assets/interface-sounds',author='Kenney',license='CC0 1.0',licenseUrl='https://creativecommons.org/publicdomain/zero/1.0/',mixPeakDbfs=float(20*np.log10(peak)),samples=[dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in assets.glob('*.ogg')])
(ep/'sfx-sources.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['ffmpeg','-y','-v','error','-i',str(ep/'final_remotion_yumemin_only.mp4'),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-t',str(n/48000),'-movflags','+faststart',str(ep/'final_remotion_yumemin_sfx.mp4')],check=True)
print('SFX cues',len(events),'duration',n/48000,'peak dBFS',record['mixPeakDbfs'])
