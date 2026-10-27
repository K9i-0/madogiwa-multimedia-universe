"""Restore local render assets from recorded source paths, without overwriting inputs."""
from pathlib import Path
import os,shutil
remotion=Path(__file__).resolve().parent
episode=remotion.parent
root=episode.parent.parent
assets={'input.mp4':root/'b00add6f490fbcdb0005bb2f101e92f4.MP4','narration.wav':episode/'clip1_line1_yume_tele_anchor.wav'}
closing=episode/'clip1_line2_yume_tele_anchor.wav'
if closing.exists():assets['closing.wav']=closing
for name,src in assets.items():
 dst=remotion/'public'/name
 if dst.exists():continue
 try:os.link(src,dst)
 except OSError:shutil.copy2(src,dst)
 print(dst)

# Restore the dialogue assets from tracked WAVs and shared character templates.
pub=remotion/'public/duo';pub.mkdir(exist_ok=True)
for src in episode.glob('duo_*_*.wav'):
 name=src.stem.split('_')[1]+'.wav'
 if not (pub/name).exists():shutil.copy2(src,pub/name)
t=root/'03_SCRIPTS/00_TEMPLATES/characters'
items=[(t/'commentary_base_20261014/yumemin_base_v1.png','yumemin.png')]
items += [(t/'commentary_duo_v1/exports'/f'yametaro_{m}_{s}.png',f'yametaro_{m}_{s}.png') for m in ['normal','bored','worry','surprise','angry'] for s in ['closed','open']]
for src,name in items:
 if not (pub/name).exists():shutil.copy2(src,pub/name)

pub=remotion/'public/sobaya';pub.mkdir(exist_ok=True)
for i in range(1,5):
 src=episode/f'sobaya_line{i}.wav'
 if src.exists() and not (pub/f's{i}.wav').exists():shutil.copy2(src,pub/f's{i}.wav')
for name in ['sobaya_normal.png','sobaya_normal_talk.png']:
 src=t/'commentary_sobaya_v2'/name
 if not (pub/name).exists():shutil.copy2(src,pub/name)
