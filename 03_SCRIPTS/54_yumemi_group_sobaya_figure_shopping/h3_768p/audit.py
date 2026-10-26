"""Validate native 768p delivery and adopted master waveform; not listening QA."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
P=Path(__file__).resolve().parent;EP=P.parent
video=EP/'final_remotion_shopping_h3_768p.mp4'
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1344,768,'24/1',720)
assert sum(s['codec_type']=='audio' for s in info['streams'])==1
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
def decode(path):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ar','48000','-ac','1','-f','f32le','-']),dtype='<f4').astype('float64')
x=decode(EP/'remotion/public/shopping_irodori_instrumental_master_30s.wav');y=decode(video);n=min(len(x),len(y));x=x[:n];y=y[:n];corr=float(np.dot(x,y)/np.sqrt(np.dot(x,x)*np.dot(y,y)))
assert corr>.98 and np.isfinite(y).all() and abs(y).max()<1
report=dict(output=video.name,sha256=hashlib.sha256(video.read_bytes()).hexdigest(),resolution=[1344,768],frames=720,fps=24,seconds=30,audioSampleRate=a['sample_rate'],audioTracks=1,audioMasterCorrelation=corr,fullDecode='passed',auditoryReview='not performed; adopted original Irodori/instrumental master reused',visualReview='pending')
(P/'delivery-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
