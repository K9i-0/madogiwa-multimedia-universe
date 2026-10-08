"""Mix the confirmed tracks on the manifest frame timeline; never substitutes missing BGM."""
from pathlib import Path
import argparse,json,subprocess,wave,hashlib
import numpy as np
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--main',type=Path);parser.add_argument('--preview-without-main',action='store_true');args=parser.parse_args()
if not args.main and not args.preview_without_main:
 candidates=list((P.parent/'input').glob('*.wav'))
 if len(candidates)==1:args.main=candidates[0]
if not args.preview_without_main and (not args.main or not args.main.is_file()):raise SystemExit('Confirmed main BGM is required.')
m=json.loads((P/'src/edit-manifest.json').read_text());sr=48000;fps=m['composition']['fps'];n=m['composition']['durationInFrames']*sr//fps

def decode(path,filters=None):
 cmd=['ffmpeg','-v','error','-i',str(path)]
 if filters:cmd+=['-af',filters]
 b=subprocess.check_output(cmd+['-f','f32le','-ar',str(sr),'-ac','2','pipe:1']);return np.frombuffer(b,dtype='<f4').reshape(-1,2).copy()
def save(path,a):
 a=np.clip(a,-1,1)
 with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32767).astype('<i2').tobytes())
def fade(a,head,tail):
 a[:head]*=np.linspace(0,1,head)[:,None];a[-tail:]*=np.linspace(1,0,tail)[:,None];return a
voice=np.zeros((n,2),np.float32)
for d in m['dialogue']:
 a=decode(P/'public'/d['audio']);start=d['startFrame']*sr//fps;voice[start:start+len(a)]+=a
save(P/'out/voice_unmixed.wav',voice)
voice=decode(P/'out/voice_unmixed.wav','loudnorm=I=-18:TP=-2:LRA=11')[:n]
if len(voice)<n:voice=np.pad(voice,((0,n-len(voice)),(0,0)))
intro=decode(P/'public/intro.mp3','loudnorm=I=-34:TP=-3:LRA=11');cut=m['mainStartFrame']*sr//fps;intro=fade(intro[:cut],sr//2,int(.8*sr));voice[:cut]+=intro
if args.main:
 main=decode(args.main,'loudnorm=I=-34:TP=-3:LRA=11')
 if len(main)<n-cut:main=np.tile(main,(int(np.ceil((n-cut)/len(main))),1))
 main=fade(main[:n-cut],int(.6*sr),sr);voice[cut:]+=main
peak=float(np.max(np.abs(voice)))
if peak>.95:voice*=.95/peak
save(P/'public/mixed.wav',voice)
# Keep a format-stable working input for a full Remotion rerender.
if args.main:
 save(P/'public/main.wav',decode(args.main))
 subprocess.run(['npx','remotion','render','src/index.ts','Explainer','out/visuals.mp4','--codec=h264','--concurrency=2','--muted','--overwrite','--log=error'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'out/visuals.mp4'),'-i',str(P/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(P.parent/('preview_explainer_pending_bgm.mp4' if args.preview_without_main else 'final_remotion_explainer_pilot_flexible.mp4'))],check=True)
record={'mainInput':str(args.main) if args.main else None,'mainSha256':hashlib.sha256(args.main.read_bytes()).hexdigest() if args.main else None,'mainStartFrame':m['mainStartFrame'],'sampleRate':sr,'voiceTargetLUFS':-18,'bgmTargetLUFS':-34,'premasterPeak':peak,'samples':n}
(P.parent/'mix_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(record)
