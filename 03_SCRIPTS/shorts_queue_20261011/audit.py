#!/usr/bin/env python3
"""Probe, decode and compare adopted audio. Does not certify listening or publish."""
from pathlib import Path
import json,hashlib,subprocess,datetime,concurrent.futures
Q=Path(__file__).resolve().parent;R=Q.parents[1]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def probe(p):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def audio_hash(p):
 return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
def check(row):
 p=R/row['output'];m=json.loads((R/row['manifest']).read_text());source=R/row['source']
 if not p.exists():return dict(slug=row['slug'],passed=False,error='Output missing')
 try:
  d=probe(p);v=next(s for s in d['streams'] if s['codec_type']=='video');a=next(s for s in d['streams'] if s['codec_type']=='audio')
  raw=probe(source);orig=next(s for s in raw['streams'] if s['codec_type']=='video')
  result=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],capture_output=True,text=True)
  checks=dict(resolution=(v['width'],v['height'])==(720,1280),under60=float(d['format']['duration'])<60,fps=v['avg_frame_rate']==orig['avg_frame_rate'],frames=int(v['nb_frames'])==m['durationInFrames'],audio=audio_hash(source)==audio_hash(p),decode=result.returncode==0 and not result.stderr.strip(),captions=all(0<=c['startFrame']<c['endFrame']<=m['durationInFrames'] and len(c['text'].splitlines())<=3 for c in m['captions']))
  return dict(slug=row['slug'],passed=all(checks.values()),checks=checks,sha256=sha(p),sourceSha256=sha(source),manifestSha256=sha(R/row['manifest']),duration=float(d['format']['duration']),width=v['width'],height=v['height'],fps=v['avg_frame_rate'],frames=int(v['nb_frames']),audioCodec=a['codec_name'],bytes=p.stat().st_size,decodeErrors=result.stderr[:600])
 except Exception as e:return dict(slug=row['slug'],passed=False,error=str(e))
def main():
 rows=json.loads((Q/'queue.json').read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:results=list(ex.map(check,rows))
 report=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='37 remaining locally produced episodes under 60 seconds; five published pilot Shorts excluded',allPassed=all(r['passed'] for r in results),listeningAudit=False,listeningNote='Original adopted audio retained byte-for-byte. ASR-assisted timestamps and source scripts used; no claim of subjective full listening.',videos=results)
 (Q/'technical-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(f"{sum(r['passed'] for r in results)}/{len(results)} passed")
 for r in results:
  if not r['passed']:print(r['slug'],r.get('error',r.get('checks')))
 return 0 if report['allPassed'] else 1
if __name__=='__main__':raise SystemExit(main())
