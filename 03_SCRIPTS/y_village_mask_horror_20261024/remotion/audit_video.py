from pathlib import Path
import hashlib,json,subprocess,re
P=Path(__file__).resolve().parent;E=P.parent
video=E/'final_remotion_horror.mp4';m=json.loads((P/'src/edit-manifest.json').read_text());n=m['composition']['durationInFrames']
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1')
assert int(v['nb_read_frames'])==n
assert abs(float(v['duration'])-n/30)<.001
assert a['sample_rate']=='48000' and a['channels']==2
decode=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(video),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True)
(P/'out/final-decode.log').write_text(decode.stderr)
assert decode.returncode==0,decode.stderr[-1000:]
assert not re.search(r'Error (while|decoding)|corrupt|Invalid data|Conversion failed',decode.stderr,re.I)
summary=decode.stderr[decode.stderr.rfind('Summary:'):]
out={'file':str(video.name),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,'video':{'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':int(v['nb_read_frames']),'duration':float(v['duration'])},'audio':{'codec':a['codec_name'],'sampleRate':a['sample_rate'],'channels':a['channels']},'decodePassed':True,'loudnessSummary':summary,'humanListening':'not performed; not inferred from ASR or decode'}
(E/'video-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
# All subtitle and shot boundaries, plus middle/longest holds, from the FINAL encoded video.
frames=set()
for row in m['captions']+m['shots']:
    frames.update([row['from']-1,row['from'],row['from']+1,row['to']-1,row['to'],(row['from']+row['to'])//2])
frames=sorted(f for f in frames if 0<=f<n)
directory=P/'out/boundaries';directory.mkdir(exist_ok=True)
expression='+'.join(f'eq(n\\,{f})' for f in frames)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f'select={expression}','-fps_mode','vfr','-q:v','3',str(directory/'%04d.jpg')],check=True)
(P/'out/boundary-frames.json').write_text(json.dumps(frames)+'\n')
print('Final-video boundary frames:',len(frames))
