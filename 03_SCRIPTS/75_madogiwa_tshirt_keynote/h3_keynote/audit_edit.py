"""Mechanical delivery QA; never labels waveform checks as listening."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
P=Path(__file__).resolve().parent;EP=P.parent;ROOT=EP.parents[1]
m=json.loads((EP/'remotion/src/edit-manifest-h3.json').read_text());video=EP/'final_remotion_h3_irodori.mp4'
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1280,720,'24/1',m['durationInFrames'])
assert len([s for s in info['streams'] if s['codec_type']=='audio'])==1
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
def audio(path):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ar','48000','-ac','1','-f','f32le','-']),dtype='<f4')
reference=audio(EP/'remotion/public'/m['audio']);actual=audio(video);n=min(len(reference),len(actual));x=reference[:n].astype('float64');y=actual[:n].astype('float64');correlation=float(np.dot(x,y)/np.sqrt(np.dot(x,x)*np.dot(y,y)))
assert correlation>.98,correlation
assert np.isfinite(actual).all() and abs(actual).max()<1
report=dict(output=str(video.relative_to(ROOT)),sha256=hashlib.sha256(video.read_bytes()).hexdigest(),width=v['width'],height=v['height'],fps=v['r_frame_rate'],frames=int(v['nb_read_frames']),seconds=m['durationInFrames']/24,fullDecode='passed',audioTracks=1,audioSampleRate=a['sample_rate'],pcmCorrelation=correlation,audioPeak=float(abs(actual).max()),adoptedDialogueLines=32,visualReview='All 32 caption stills and source start/middle/end inspected; ch13 double-image interval removed',auditoryReview='Not performed; original adopted Irodori WAVs reused, waveform and timing checks only',lipSync='Rigid mask; fine gesture/speech synchronization not verified',colab='stopped',remainingVisualLimitations=['ch08 includes a generated push-in to presenter instead of fixed wide shot','ch13 is cut between two static product-detail layouts; no screen replacement'])
(P/'edit-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
