from pathlib import Path
from psd_tools import PSDImage
import shutil
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
CACHE=ROOT/'.local/voicevox-explainer'
PUBLIC=P/'public'
def select(group,name):
 for l in group:l.visible=l.name==name
for who in ['zunda','metan']:
 psd=PSDImage.open(next((CACHE/who).rglob('*.psd')))
 groups={l.name:l for l in psd}
 select(groups['!眉'],'*普通眉' if who=='zunda' else '*ごきげん')
 if who=='metan':
  outfit=groups['*白ロリ服'];select(next(l for l in outfit if l.name=='!左腕'),'*普通')
 for mood in ['normal','blink','surprise']:
  select(groups['!目'],('*UU' if who=='zunda' else '*目閉じ') if mood=='blink' else ('*〇〇' if who=='zunda' else '*○○') if mood=='surprise' else '*目セット')
  for talking in [False,True]:
   select(groups['!口'],('*ほあー' if talking else '*むふ') if who=='zunda' else ('*わあー' if talking else '*ほほえみ'))
   img=psd.composite(force=True)
   box=(160,80,980,1130) if who=='zunda' else (90,0,990,1150)
   img=img.crop(box);img.thumbnail((450,580));img.save(PUBLIC/f'{who}_{mood}_{int(talking)}.png')
for i in [1,2,3,4]:
 shutil.copyfile(ROOT/f'01_WORLD/story_timeline/episode_{i:02}.png',PUBLIC/f'episode_{i:02}.png')
shutil.copyfile(CACHE/'intro.mp3',PUBLIC/'intro.mp3')
print('Assets ready')
