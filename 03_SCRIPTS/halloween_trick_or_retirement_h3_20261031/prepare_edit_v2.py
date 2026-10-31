"""Speaker-focused H3 re-edit. Originals and v1 remain intact."""
from pathlib import Path
import json, subprocess, math
EP=Path(__file__).resolve().parent
PUB=EP/'remotion/public'
def duration(p):
 return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
segments=[];captions=[];cursor=0
def shot(id,file,trim,n,audio=None,at=0,crop=None,speaker=None,text=None):
 global cursor
 s=dict(id=id,file=file,trimStartFrame=round(trim*24),durationInFrames=n,startFrame=cursor,audioFile=audio or file,audioTrimStartFrame=round(at*24),crop=crop or [0,0,864,480])
 segments.append(s)
 if text:captions.append(dict(startFrame=cursor,endFrame=cursor+n,speaker=speaker,text=text))
 cursor+=n
threat=math.ceil(duration(EP/'v2_sobaya_threat.wav')*24)
last=math.ceil(duration(EP/'v2_sobaya_final.wav')*24)
shot('entrance','ch01_480p.mp4',0,192)
shot('chant','ch02_480p.mp4',0,48,at=0,speaker='全員',text='トリック・オア・退職！')
shot('sobaya_threat','ch02_480p.mp4',2,threat,audio='../v2_sobaya_threat.wav',crop=[290,0,340,191.25],speaker='そば屋',text='お菓子をくれなきゃ、退職しちゃうぞ！')
shot('fired_reaction','ch02_480p.mp4',8,64,audio='ch03_480p.mp4',at=0,crop=[50,125,350,196.875],speaker='とーくん（声）',text='うん。三人ともクビです。')
shot('yametaro_reply','ch03_480p.mp4',2.75,128,at=64/24,crop=[472,120,392,220.5],speaker='やめ太郎',text='いや、そこはお菓子くれる流れやん。')
shot('tokun_door','ch03_480p.mp4',8,96,at=8,crop=[0,0,548,308.25],speaker='とーくん',text='会社のドア壊したよね？')
shot('outside_establish','ch04_480p.mp4',0,18,at=0,speaker='やめ太郎',text='お菓子もろてへんのに、\nイタズラされたんワイらやん。')
shot('yametaro_outside','ch04_480p.mp4',.75,70,at=.75,crop=[550,190,314,176.625],speaker='やめ太郎',text='お菓子もろてへんのに、\nイタズラされたんワイらやん。')
shot('sobaya_final','ch04_480p.mp4',7,last,audio='../v2_sobaya_final.wav',crop=[0,0,350,196.875],speaker='そば屋',text='明日から毎日ハロウィンできますね！')
shot('takosan_silence','ch04_480p.mp4',11,48,audio='SILENCE',crop=[282,198,320,180])
for s in segments:
 assert s['trimStartFrame']+s['durationInFrames'] <= round(duration(PUB/s['file'])*24), s['id']
 x,y,w,h=s['crop']; assert x>=0 and y>=0 and x+w<=864 and y+h<=480, s['id']
assert all(0<=c['startFrame']<c['endFrame']<=cursor for c in captions)
m=dict(composition=dict(id='Halloween',width=1280,height=720,fps=24,durationInFrames=cursor),segments=segments,captions=captions)
(EP/'remotion/src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
args=['ffmpeg','-y','-v','error'];filters=[];idx=0
for i,s in enumerate(segments):
 d=s['durationInFrames']/24
 if s['audioFile']=='SILENCE':filters.append(f'anullsrc=r=48000:cl=stereo,atrim=duration={d}[a{i}]');continue
 p=EP/s['audioFile'][3:] if s['audioFile'].startswith('../') else PUB/s['audioFile']
 args+=['-i',str(p)]
 gain=',loudnorm=I=-18:TP=-2:LRA=7' if p.suffix=='.wav' else ''
 filters.append(f'[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start={s["audioTrimStartFrame"]/24}:duration={d},asetpts=PTS-STARTPTS{gain},apad,atrim=duration={d},afade=t=in:d=0.008,afade=t=out:st={d-.015}:d=0.015[a{i}]');idx+=1
filters.append(''.join(f'[a{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=0:a=1[master]')
subprocess.run(args+['-filter_complex',';'.join(filters),'-map','[master]','-c:a','pcm_s16le',str(PUB/'master.wav')],check=True)
print('V2 duration',cursor/24,'Sobaya durations',threat/24,last/24)
