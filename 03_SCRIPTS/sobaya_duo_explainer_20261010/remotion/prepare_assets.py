from pathlib import Path
import shutil
p=Path(__file__).resolve().parent;root=p.parents[2];pub=p/'public';pub.mkdir(exist_ok=True)
pack=root/'03_SCRIPTS/00_TEMPLATES/characters/commentary_duo_v1'
(pub/'sprites').mkdir(exist_ok=True)
for f in pack.glob('*.png'):shutil.copy2(f,pub/'sprites'/f.name)
shutil.copy2(root/'03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png',pub/'sobaya_sheet.png')
for n,ext in [(1,'png'),(3,'png'),(4,'png'),(5,'png'),(6,'jpeg'),(8,'png'),(12,'png')]:shutil.copy2(root/f'01_WORLD/story_timeline/episode_{n:02}.{ext}',pub/f'episode_{n:02}.{ext}')
