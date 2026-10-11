#!/usr/bin/env python3
"""Rebuild separate subtitle-free picture sources. Adopted masters and audio are never overwritten."""
from pathlib import Path
import argparse,json,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[1]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('episodes',nargs='*');args=ap.parse_args()
 jobs=json.loads((Q/'clean-jobs.json').read_text())
 if args.episodes:
  known={j['episode'] for j in jobs};unknown=set(args.episodes)-known
  if unknown:ap.error('Unknown episode: '+', '.join(sorted(unknown)))
 for j in jobs:
  if args.episodes and j['episode'] not in args.episodes:continue
  cwd=R/'03_SCRIPTS'/j['episode']/'remotion'
  subprocess.run(['npx','remotion','render','src/shorts-clean.tsx',j['composition'],'out/shorts-clean.mp4','--codec=h264','--crf=16','--concurrency=2','--muted',*j.get('extraArgs',[])],cwd=cwd,check=True)
if __name__=='__main__':main()
