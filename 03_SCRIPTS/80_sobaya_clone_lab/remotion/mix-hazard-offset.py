"""Create a music-offset comparison without re-encoding the adopted picture."""
from pathlib import Path
import subprocess,json,hashlib
r=Path(__file__).resolve().parent
m=json.loads((r/'src/hazard-bgm22.json').read_text())
out=r.parent/m['output'];duration=m['durationFrames']/m['fps'];start=m['musicStartFrame']/m['fps']
af=f"atrim=start={start}:duration={duration},asetpts=PTS-STARTPTS,volume=0.56,afade=t=in:d=0.15,afade=t=out:st={duration-.45}:d=0.45,alimiter=limit=0.84:level=false:latency=true"
subprocess.run(['ffmpeg','-v','error','-y','-i',str(r.parent/m['pictureSource']),'-i',str(r/m['musicSource']),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',af,'-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(out)],check=True)
def video_hash(f):return subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
assert video_hash(out)==video_hash(r.parent/m['pictureSource'])
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]));v=next(s for s in d['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['nb_frames'])==(720,1280,'972')
assert abs(float(d['format']['duration'])-duration)<.05
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
q={'output':out.name,'sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'musicRangeSeconds':[start,start+duration],'durationSeconds':duration,'sameVideoBitstream':True,'fullDecode':'passed','subjectiveAudition':False,'note':'Music-offset comparison; original beat animations and shot timing retained, not re-aligned to the new music segment.'}
(r.parent/'aura_phonk_prep_20261026/hazard-bgm22-qa.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False,indent=2))
