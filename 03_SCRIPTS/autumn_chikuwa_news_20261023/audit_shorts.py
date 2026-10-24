from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).resolve().parent
v=P/'final_remotion_shorts_9x16.mp4';main=P/'final_remotion_news.mp4'
def run(a):return subprocess.run(list(map(str,a)),capture_output=True,check=True)
probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',v]).stdout);vs=next(s for s in probe['streams'] if s['codec_type']=='video');assert (vs['width'],vs['height'],vs['r_frame_rate'],int(vs['nb_read_frames']))==(720,1280,'30/1',1771)
def audio(f):return hashlib.sha256(run(['ffmpeg','-v','error','-i',f,'-map','0:a:0','-c','copy','-f','adts','-']).stdout).hexdigest()
a=audio(main);b=audio(v);assert a==b
run(['ffmpeg','-v','error','-i',v,'-f','null','-'])
audit=dict(resolution=[720,1280],fps=30,frames=1771,seconds=1771/30,sha256=hashlib.sha256(v.read_bytes()).hexdigest(),audioStreamSha256=b,audioIdenticalToApprovedMaster=True,fullDecode='pass',generationRequests=0,sharedTemplate='03_SCRIPTS/shorts_queue_20261011/remotion/src/index.tsx',captions='Original four speech cards moved below clean footage; broadcast news graphics retained.',listeningAudit='No new listening claimed; approved master AAC stream copied unchanged.')
(P/'shorts_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');print(json.dumps(audit,ensure_ascii=False))
