from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
bg=Image.new('RGBA',(1280,720),'#102335')
src=Image.open(P.parent/'game_capture.png').convert('RGBA')
bg.alpha_composite(src.resize((1460,671),Image.Resampling.LANCZOS),(-90,-150))
overlay=Image.open(P/'overlay_b_refined.png').convert('RGBA')
assert overlay.getextrema()[3][0]==0
final=Image.alpha_composite(bg,overlay.resize((1280,720),Image.Resampling.LANCZOS)).convert('RGB')
final.save(P/'thumbnail_b_refined.png')
final.save(P/'thumbnail_b_refined.jpg',quality=95,subsampling=0)
