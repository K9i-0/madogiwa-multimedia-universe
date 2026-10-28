"""Check deliverable structure, full decode, timeline and capture edit boundaries."""
import hashlib, json, math, subprocess
from pathlib import Path

EP=Path(__file__).resolve().parent
M=json.loads((EP/'remotion/src/edit-manifest.json').read_text())
assert not M['pending'], M['pending']
fps=M['composition']['fps'];frames=M['composition']['durationInFrames']
cursor=0
for s in M['segments']:
    assert s['start']==cursor and s['duration']>0
    cursor+=s['duration']
assert cursor==frames
previous=0
for c in M['captions']:
    assert 0<=c['start']<c['end']<=frames
    assert c['start']>=previous
    previous=c['end']
video=EP/'final_remotion_mega_dvd.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)],text=True))
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(960,720)
assert v['r_frame_rate']=='24/1' and int(v['nb_read_frames'])==frames
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
assert a['codec_name']=='aac' and a['sample_rate']=='48000'
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
measurement=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-af','loudnorm=I=-18:TP=-1:LRA=11:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
loudness=json.JSONDecoder().raw_decode(measurement.stderr[measurement.stderr.rfind('{'):])[0]
assert math.isfinite(float(loudness['input_i'])) and float(loudness['input_tp'])<0
out=EP/'generated/final-audit';out.mkdir(parents=True,exist_ok=True)
points={0,frames-1}
for s in M['segments']:
    points.update([max(0,s['start']-1),s['start'],s['start']+1,s['start']+s['duration']//2,s['start']+s['duration']-1])
for c in M['captions']:
    points.update([max(0,c['start']-1),c['start'],c['start']+1,c['end']-1,c['end']])
for f in sorted(points):
    if f>=frames:continue
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(f/fps),'-i',str(video),'-frames:v','1',str(out/f'frame-{f:04d}.png')],check=True)
report={'output':str(video.relative_to(EP)),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'duration_seconds':frames/fps,'frames':frames,'width':v['width'],'height':v['height'],'fps':fps,'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'sample_rate':a['sample_rate'],'full_decode':'passed','timeline':'passed','loudness':loudness,'boundary_frames':sorted(points),'visual_audit':'pending final encoded review','listening_and_precise_lipsync':'not performed; ASR and still-frame inspection are separate checks'}
(EP/'production-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['output','duration_seconds','frames','width','height','full_decode','timeline']},ensure_ascii=False))
