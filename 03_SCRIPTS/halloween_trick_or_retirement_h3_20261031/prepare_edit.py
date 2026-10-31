"""Use native H3 audio; remove unrequested tail and cover malformed opening with reaction footage."""
from pathlib import Path
import json,subprocess
EP=Path(__file__).resolve().parent
pub=EP/'remotion/public'
raw=[
 ('entrance','ch01_480p.mp4',0,192,None,0),
 ('threat','ch02_480p.mp4',0,120,None,0),
 ('fired_reaction','ch02_480p.mp4',194,66,'ch03_480p.mp4',0),
 ('fired_reply','ch03_480p.mp4',66,222,None,66),
 ('outside','ch04_480p.mp4',0,168,None,0),
 ('outside_reaction','ch04_480p.mp4',264,48,None,264),
]
segments=[];start=0
for id,file,trim,duration,audio,audiotrim in raw:
 segments.append(dict(id=id,file=file,trimStartFrame=trim,durationInFrames=duration,startFrame=start,audioFile=audio or file,audioTrimStartFrame=audiotrim))
 start+=duration
captions=[]
def cap(a,b,who,text):captions.append(dict(startFrame=round(a*24),endFrame=round(b*24),speaker=who,text=text))
cap(8,10,'全員','トリック・オア・退職！')
cap(10,13,'そば屋','お菓子をくれなきゃ、退職しちゃうぞ！')
cap(13,15.66,'とーくん','うん。三人ともクビです。')
cap(15.66,21,'やめ太郎','いや、そこはお菓子くれる流れやん。')
cap(21,24.2,'とーくん','会社のドア壊したよね？')
outside=next(s['startFrame']/24 for s in segments if s['id']=='outside')
cap(outside,outside+3.44,'やめ太郎','お菓子もろてへんのに、\nイタズラされたんワイらやん。')
cap(outside+3.9,outside+6.9,'そば屋','明日から……明日から毎日ハロウィンできますね！')
m=dict(composition=dict(width=1280,height=720,fps=24,durationInFrames=start),segments=segments,captions=captions)
(EP/'remotion/src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
args=['ffmpeg','-y','-v','error'];filters=[]
for i,s in enumerate(segments):
 args+=['-i',str(pub/s['audioFile'])]
 filters.append(f'[{i}:a]aresample=48000,atrim=start={s["audioTrimStartFrame"]/24}:duration={s["durationInFrames"]/24},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={s["durationInFrames"]/24-.008}:d=0.008[a{i}]')
filters[-1]=f'anullsrc=r=48000:cl=stereo,atrim=duration=2[a{len(segments)-1}]'
filters.append(''.join(f'[a{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=0:a=1,afade=t=out:st={start/24-.5}:d=0.5[master]')
subprocess.run(args+['-filter_complex',';'.join(filters),'-map','[master]','-c:a','pcm_s16le',str(pub/'master.wav')],check=True)
print(json.dumps(m,ensure_ascii=False,indent=2))
