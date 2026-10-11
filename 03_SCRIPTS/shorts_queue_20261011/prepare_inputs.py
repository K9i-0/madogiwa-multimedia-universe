#!/usr/bin/env python3
"""Recreate ignored public hardlinks without changing approved source media."""
from pathlib import Path
import json, os, shutil
Q=Path(__file__).resolve().parent
R=Q.parents[1]

def main():
    public=Q/'remotion/public';public.mkdir(parents=True,exist_ok=True)
    rows=json.loads((Q/'queue.json').read_text())
    for row in rows:
        manifest=json.loads((R/row['manifest']).read_text())
        for clip in manifest['clips']:
            source=R/clip['source'];target=public/clip['file']
            if not source.is_file():raise SystemExit(f'Missing source: {source}; see clean-jobs.json and README.md')
            if target.exists():
                if source.stat().st_ino==target.stat().st_ino and source.stat().st_dev==target.stat().st_dev:continue
                # Rebuilt clean renders replace old inodes: refresh only the generated link.
                target.unlink()
            try:os.link(source,target)
            except OSError:shutil.copy2(source,target)
    print(f'Inputs ready for {len(rows)} Shorts')
if __name__=='__main__':main()
