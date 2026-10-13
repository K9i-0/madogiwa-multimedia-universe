"""Check reference continuity and the full news clip in the actual encoded MP4."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import argparse
import subprocess
import numpy as np
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--source', default='out/review_v7_04.mp4')
parser.add_argument('--tag', default='v7_04')
args = parser.parse_args()
src = P / args.source
out = P / 'out' / f'audit_{args.tag}'
out.mkdir(exist_ok=True)
m = json.loads((P / 'src/edit-manifest.json').read_text())
points = []
for id in ['v001', 'v014', 'v042', 'v053', 'v064', 'v066', 'v070']:
    d = next(d for d in m['dialogue'] if d['id'] == id)
    for offset in [-1, 0, 1, 8]:
        points.append({'group': id, 'name': f'{id}_{offset}', 'frame': d['startFrame'] + offset})
for id in ['v053', 'v064', 'v065', 'v069']:
    d = next(d for d in m['dialogue'] if d['id'] == id)
    for i, s in enumerate(d['captionSegments'][1:], 1):
        for offset in [-1, 0, 1]:
            group = f'{id}_page{i}'
            points.append({'group': group, 'name': f'{group}_{offset}', 'frame': d['startFrame'] + s['startFrame'] + offset})
groups = {}
for point in points:
    groups.setdefault(point['group'], []).append(point)
news = next(c for c in m['clips'] if c['id'] == 'example_news')
assert news['durationInFrames'] == 900 and news['sourceStartFrame'] == 0
for offset in [-1, 0, 450, 899, 900]:
    points.append({'name': f'news_{offset}', 'frame': news['startFrame'] + offset})
points.append({'name': 'last', 'frame': m['composition']['durationInFrames'] - 1})

def extract(point):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(point['frame']/30),
                    '-i', str(src), '-frames:v', '1', str(out / (point['name'] + '.png'))], check=True)

with ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(extract, points))
report = []
for group, selected in groups.items():
    arrays = [np.asarray(Image.open(out / (p['name'] + '.png')).convert('RGB').crop((280, 24, 1000, 550)), dtype=float) for p in selected]
    differences = [float(np.abs(a-arrays[0]).mean()) for a in arrays[1:]]
    # Compression or JPEG decoding can cause subpixel-level differences; a fade
    # to the background causes a large discontinuity, far above this threshold.
    assert max(differences) < 1, (group, differences)
    report.append({'group': group, 'frames': [p['frame'] for p in selected], 'meanAbsolutePixelDifferences': differences})
selected = [p for p in points if p['name'] in ['v001_-1', 'v001_0', 'v064_-1', 'v064_0', 'news_0', 'news_450', 'news_899', 'news_900']]
canvas = Image.new('RGB', (1280, 1560), 'white')
draw = ImageDraw.Draw(canvas)
for i, point in enumerate(selected):
    x, y = (i%2)*640, (i//2)*390
    canvas.paste(Image.open(out / (point['name'] + '.png')).resize((640, 360)), (x, y))
    draw.text((x+8, y+365), f"{point['name']} | frame {point['frame']}", fill='black')
canvas.save(out / 'revision_contact.jpg')
(out / 'continuity.json').write_text(json.dumps(report, indent=2))
(out / 'points.json').write_text(json.dumps(points, indent=2))
print('PASS: actual MP4 reference continuity at', len(groups), 'boundaries;', len(points), 'frames extracted')
