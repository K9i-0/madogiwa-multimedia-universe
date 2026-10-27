"""Sample the encoded delivery at every caption and each other lesson layout."""
import hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw

EP=Path(__file__).resolve().parent
m=json.loads((EP/'remotion/src/edit-manifest.json').read_text())
video=EP/m['outputFile'];out=EP/'generated/audit-r2/encoded';out.mkdir(parents=True,exist_ok=True)
shots={}
for cue in m['captions']:
    frame=(cue['start']+cue['end'])//2
    segment=next(s for s in m['segments'] if s['start']<=frame<s['start']+s['duration'])
    shots[frame]=segment['id']+' | caption'
for segment in m['segments']:
    if segment['type'] in ('opening','title','question','answer','ending'):
        offset=100 if segment['type']=='opening' else segment['duration']-50 if segment['type']=='ending' else segment['duration']//2
        shots[segment['start']+offset]=segment['id']
frames=sorted(shots)
expression='+'.join(f'eq(n,{frame})' for frame in frames)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf',f"select='{expression}'",
                '-fps_mode','vfr',str(out/'frame-%03d.png')],check=True)
pages=[]
for first in range(0,len(frames),8):
    page=Image.new('RGB',(1280,1528),'#ffffff');draw=ImageDraw.Draw(page)
    for offset,frame in enumerate(frames[first:first+8]):
        image=Image.open(out/f'frame-{first+offset+1:03d}.png');image.thumbnail((640,360))
        x=offset%2*640;y=offset//2*382
        page.paste(image,(x,y));seconds=frame/24
        draw.text((x+8,y+362),f'{first+offset+1:02d} | {seconds//60:02.0f}:{seconds%60:05.2f} | {shots[frame]}',fill='#111111')
    name=f'contact-{first//8+1:02d}.jpg';page.save(out/name,quality=94);pages.append(name)
(out/'manifest.json').write_text(json.dumps({'video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
    'frames':[{'frame':frame,'seconds':frame/24,'label':shots[frame]} for frame in frames],
    'pages':pages,'note':'Image extraction only. Human/model inspection is a separate step; this script does not assert visual quality.'},ensure_ascii=False,indent=2)+'\n')
print(f'Extracted {len(frames)} encoded frames into {len(pages)} contact sheets: {out}')
