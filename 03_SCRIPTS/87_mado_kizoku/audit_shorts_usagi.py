from pathlib import Path
import json,hashlib,subprocess
P=Path(__file__).resolve().parent;V=P/'final_remotion_shorts_usagi_9x16.mp4';S=P/'final_remotion_subtitles_v12_usagi_normal.mp4';M=json.loads((P/'shorts-manifest-usagi.json').read_text());O=P/'remotion/out/shorts-usagi-audit';O.mkdir(parents=True,exist_ok=True)
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(V)]));v=next(x for x in d['streams'] if x['codec_type']=='video')
assert (v['width'],v['height'],v['nb_read_frames'],v['r_frame_rate'])==(720,1280,'1102','30/1')
def audiohash(p):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-t',str(1102/30),'-c','copy','-f','adts','-'])).hexdigest()
a=audiohash(V);assert a==audiohash(S)
subprocess.run(['ffmpeg','-v','error','-i',str(V),'-f','null','-'],check=True)
frames=[0,1101]+[(c['startFrame']+c['endFrame'])//2 for c in M['captions']]
for f in frames:subprocess.run(['ffmpeg','-v','error','-y','-ss',str(f/30),'-i',str(V),'-frames:v','1',str(O/f'{f}.png')],check=True)
r={'output':V.name,'sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'frames':1102,'seconds':1102/30,'width':720,'height':1280,'fps':30,'audioAACHash':a,'adoptedV12AudioIdentical':True,'fullDecode':'pass','auditFrames':frames,'listening':'User approved horizontal v12; no independent subjective listening for Shorts.'}
(P/'shorts-usagi-qa.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(r)
