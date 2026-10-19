from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2]
bgpath=R/'16_MADOGIWA_STUDIO/public/site/ogp-balcony-20260912.jpg'
before=hashlib.sha256(bgpath.read_bytes()).hexdigest();source=Image.open(bgpath).convert('RGB')
overlay=Image.open(P/'overlay_project_intro_v3.png').convert('RGBA')
alpha=np.array(overlay.getchannel('A'));assert alpha.min()==0 and alpha.max()==255
# Deterministic fit: retain entire OGP composition, no crop or generative changes.
W,H=1920,1080;background=Image.new('RGBA',(W,H),'#0c1729')
fitted=ImageOps.contain(source,(W,H),Image.Resampling.LANCZOS);background.paste(fitted,((W-fitted.width)//2,0))
foreground=Image.new('RGBA',(W,H),(0,0,0,0))
# Separate only transparent-margin regions; neither component intersects the other.
header=overlay.crop((0,0,overlay.width,220));box=header.getchannel('A').point(lambda v: 255 if v > 32 else 0).getbbox();assert box;header=header.crop(box)
header=header.resize((520,round(header.height*520/header.width)),Image.Resampling.LANCZOS)
foreground.alpha_composite(header,(950,15))
lower=overlay.crop((0,220,overlay.width,overlay.height));lower=lower.resize((W,round(lower.height*W/lower.width)),Image.Resampling.LANCZOS)
foreground.alpha_composite(lower,(0,H-lower.height))
foreground.save(P/'overlay_layout_v3.png')
result=Image.alpha_composite(background,foreground).convert('RGB');result.save(P/'thumbnail_project_intro_v3.png');result.save(P/'thumbnail_project_intro_v3.jpg',quality=92,subsampling=0)
# Pixel-level proof: outside the alpha layer, background is exactly the fitted OGP.
transparent=np.array(foreground.getchannel('A'))==0
maxdiff=int(np.max(np.abs(np.array(result).astype(int)[transparent]-np.array(background.convert('RGB')).astype(int)[transparent])))
assert maxdiff==0
assert hashlib.sha256(bgpath.read_bytes()).hexdigest()==before
(P/'composition_v3.json').write_text(json.dumps(dict(background=str(bgpath.relative_to(R)),backgroundSha256=before,sourceDimensions=list(source.size),outputDimensions=[W,H],fitDimensions=list(fitted.size),backgroundProcessing='Pillow Lanczos contain, no crop; navy padding at bottom; no generative editing',overlay='overlay_project_intro_v3.png',overlaySourceDimensions=list(overlay.size),overlayAlphaZeroPixels=int((alpha==0).sum()),maxPixelDifferenceOutsideOverlay=maxdiff,sourceFileUnchanged=True,jpeg='thumbnail_project_intro_v3.jpg',png='thumbnail_project_intro_v3.png',generator='image_gen for transparent foreground only',prompt='prompt_v3.txt'),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(dimensions=result.size,transparentPixels=int((alpha==0).sum()),uncoveredBackgroundMaxDifference=maxdiff,jpegBytes=(P/'thumbnail_project_intro_v3.jpg').stat().st_size)))
