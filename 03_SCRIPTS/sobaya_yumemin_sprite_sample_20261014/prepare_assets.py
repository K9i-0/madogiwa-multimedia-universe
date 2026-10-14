from pathlib import Path
import os
EP=Path(__file__).resolve().parent; ROOT=EP.parents[1];pub=EP/'remotion/public';pub.mkdir(parents=True,exist_ok=True)
files=[(f,f.name) for f in (ROOT/'03_SCRIPTS/00_TEMPLATES/characters/commentary_sobaya_v1').glob('sobaya_*.png')]
files += [(ROOT/'03_SCRIPTS/00_TEMPLATES/characters/commentary_base_20261014/yumemin_base_v1.png','yumemin.png')]
files += [(f,f.name) for f in EP.glob('line*.wav')]
files += [(f,f.name) for f in (ROOT/'03_SCRIPTS/00_TEMPLATES/characters/commentary_expression_20261014').glob('*.png')]
for src,name in files:
 dst=pub/name
 if not dst.exists():os.link(src,dst)

# Current Sobaya set: beer is part of the normal pose.
current=ROOT/'03_SCRIPTS/00_TEMPLATES/characters/commentary_sobaya_v2'
(pub/'sobaya_v2').mkdir(exist_ok=True)
for src in current.glob('*.png'):
 dst=pub/'sobaya_v2'/src.name
 if not dst.exists():os.link(src,dst)
