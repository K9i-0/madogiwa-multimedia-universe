from pathlib import Path
import json,subprocess
r=Path('03_SCRIPTS/80_sobaya_clone_lab/remotion')
spec=[('discovery',120,90,180,1300,.5,.5),('witness',90,180,255,1100,.6,.6),('corridor',60,255,348,1200,.5,.5),('scan',60,348,540,1000,.5,.5),('reveal',80,540,620,1600,.5,.5),('command',40,680,740,1050,.5,.5),('hold',15,740,740,1050,.5,.5),('windup',20,754,780,1700,.5,.4),('shatter',60,780,806,1700,.4,.25),('release',45,806,829,1500,.3,.4),('chase',165,829,939,1050,.5,.5),('shards',45,780,815,1700,.4,.25),('army',45,815,845,1250,.4,.45),('master',45,680,725,1050,.5,.5),('pursuit',45,870,915,1100,.5,.5),('lastimpact',45,780,810,1500,.4,.25),('title',70,829,829,1400,.38,.38)]
a=[];f=0
for name,d,start,end,w,x0,x1 in spec:
 a.append({'id':name,'from':f,'duration':d,'sourceStart':start,'sourceEnd':end,'rate':(end-start)/d,'width':w,'x0':x0,'x1':x1});f+=d
m={'composition':{'width':720,'height':1280,'fps':30,'durationInFrames':f},'segments':a,'music':{'file':'aura/revenge.wav','startFrame':0,'impactFrame':485,'beatFrames':[485,502,516,532,547,561,576,590,605,620,634,651,662,720,748,759,770,781,792,804,815,833,847,867,889,900,917,931,945,960,971,983,993,1005,1016,1029,1041]},'captions':[],'originalAudio':False,'textCards':[{'from':286,'to':330,'text':'ANOMALY DETECTED'},{'from':986,'to':1047,'text':'CLONE LAB'}],'output':'final_remotion_aura_cinematic_9x16.mp4','notes':'35 seconds; original dialogue and SFX muted; opening source 90; discovery to build-up to music impact16.16s; replay montage and title ending'}
(r/'src/aura-cinematic.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(f)

subprocess.run(["ffmpeg","-v","error","-ss",str(740/30),"-i",str(r/"public/aura/source.mp4"),"-frames:v","1","-y",str(r/"public/aura/command-hold.jpg")],check=True)
