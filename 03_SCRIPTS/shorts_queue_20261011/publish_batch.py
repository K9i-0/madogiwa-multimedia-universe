#!/usr/bin/env python3
"""Publish a named group of at most five prepared Shorts to YouTube only; default dry-run."""
from pathlib import Path
import argparse,json,hashlib,subprocess,fcntl
Q=Path(__file__).resolve().parent;R=Q.parents[1]
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',type=int,required=True);ap.add_argument('--upload',action='store_true');args=ap.parse_args()
 rows=[r for r in json.loads((Q/'queue.json').read_text()) if r['batch']==args.batch]
 if not 1<=len(rows)<=5:ap.error('Choose an existing batch of 1–5 videos.')
 audit=json.loads((Q/'technical-audit.json').read_text());checked={r['slug']:r for r in audit['videos']}
 visual=json.loads((Q/'visual-audit.json').read_text())
 if not visual['passed']:raise SystemExit('Visual audit incomplete')
 viewed={r['slug']:r for r in visual['videos']}
 # Entire batch validated before the first external write.
 for r in rows:
  a=checked[r['slug']]
  if not viewed.get(r['slug'],{}).get('passed') or viewed[r['slug']]['sha256']!=a.get('sha256'):raise SystemExit('Stale visual audit: '+r['slug'])
  if not a['passed'] or digest(R/r['output'])!=a['sha256'] or digest(R/r['manifest'])!=a['manifestSha256']:raise SystemExit('Stale or failed audit: '+r['slug'])
  meta=json.loads((Q/r['metadata']).read_text())
  if meta['status']['privacyStatus']!='public':raise SystemExit('Unexpected visibility; inspect metadata')
  print(f"batch {args.batch}: {r['title']} ({a['duration']:.2f}s) -> {r['output']}")
 if not args.upload:print('Dry-run only. Add --upload when instructed to register this batch.');return
 record_dir=Q/'youtube_uploads';record_dir.mkdir(exist_ok=True)
 with (record_dir/'.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise SystemExit('Another batch upload is already running')
  for r in rows:
   record=record_dir/(r['slug']+'.json')
   subprocess.run(['python3',str(R/'16_MADOGIWA_STUDIO/tools/upload-youtube.py'),str(R/r['output']),'--metadata',str(Q/r['metadata']),'--record',str(record)],check=True)
 print('Upload records saved. Verify YouTube processing succeeded/public via the existing YouTube connector before reporting completion. Studio was not modified.')
if __name__=='__main__':main()
