"""Frame-accurate source assembly. One Lanczos resize to delivery size."""
from pathlib import Path
import subprocess,json,sys
P=Path(__file__).resolve().parent
M=json.loads((P/'remotion/src/edit-manifest.json').read_text())
fps=M['composition']['fps'];work=P/'generated/assembly';work.mkdir(exist_ok=True,parents=True)
clips=[]
for s in M['segments']:
 source=P/s['source'];out=work/(s['id']+'.mp4');clips.append(out)
 if not source.exists():
  if '--prepare' in sys.argv:continue
  raise FileNotFoundError(source)
 stamp=json.dumps({'source':str(source),'mtime':source.stat().st_mtime_ns,**s},sort_keys=True)
 side=out.with_suffix('.stamp')
 if out.exists() and side.exists() and side.read_text()==stamp:continue
 n=s['duration'];seconds=n/fps
 vf=f"fps={fps},trim=start_frame={s['sourceStart']}:end_frame={s['sourceStart']+n},setpts=PTS-STARTPTS,scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1"
 af=f"atrim=start={s['sourceStart']/fps}:duration={seconds},asetpts=PTS-STARTPTS,aresample=48000,volume={s['volume']},afade=t=in:d=0.012,afade=t=out:st={max(0,seconds-0.035)}:d=0.035,apad,atrim=duration={seconds}"
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vf',vf,'-af',af,'-frames:v',str(n),'-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','pcm_s16le','-ac','2','-f','matroska',str(out)],check=True)
 side.write_text(stamp);print('PREPARED',s['id'],flush=True)
if '--prepare' in sys.argv:sys.exit(0)
concat=work/'concat.txt';concat.write_text(''.join("file '"+str(c)+"'\n" for c in clips))
master=P/'remotion/public/master.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(master)],check=True)
M['pending']=[];(P/'remotion/src/edit-manifest.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n')
print(master)
