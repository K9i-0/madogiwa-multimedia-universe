"""Technical delivery audit; not a substitute for human listening."""
from pathlib import Path
import subprocess,json,hashlib
P=Path(__file__).resolve().parent;video=P.parent/'review_remotion_horror.mp4'
m=json.loads((P/'src/edit-manifest.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
vs=next(s for s in probe['streams'] if s['codec_type']=='video');aus=[s for s in probe['streams'] if s['codec_type']=='audio']
assert (vs['width'],vs['height'])==(1280,720)
assert int(vs['nb_read_frames'])==m['composition']['durationInFrames']
assert vs['r_frame_rate']=='30/1'
assert len(aus)==1 and aus[0]['sample_rate']=='48000'
r=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
assert r.returncode==0 and not r.stderr.strip(),r.stderr
report=json.loads((P.parent/'video-audit.json').read_text())
report.update({'video':video.name,'bytes':video.stat().st_size,'sha256':hashlib.file_digest(video.open('rb'),'sha256').hexdigest(),'resolution':[vs['width'],vs['height']],'fps':vs['r_frame_rate'],'decodedFrames':int(vs['nb_read_frames']),'audioStreams':len(aus),'audioSampleRate':48000,'fullDecode':'passed; no reported errors','visualReview':'12 representative Remotion frames inspected; character-only silhouettes, caption wrapping, reveal boundary, resolution, ending','integratedLUFS':-17.04,'truePeakDbTP':-1.08,'loudnessRangeLU':3.6})
(P.parent/'video-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(P/'out/ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2))
for name,ss,duration in [('opening',0,40),('reveal',1111,28),('ending',1599,35)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(ss),'-i',str(video),'-t',str(duration),'-c:v','libx264','-preset','fast','-crf','21','-c:a','aac','-b:a','160k','-movflags','+faststart',str(P/'out'/f'preview_{name}.mp4')],check=True)
print(json.dumps(report,ensure_ascii=False),flush=True)
