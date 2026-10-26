from pathlib import Path
import json,os
r=Path(__file__).resolve().parent;p=r.parent
src=p/'wan3_pov_replacement_seed26092680_480p.mp4';dst=r/'public/aura/pov-full.mp4'
if not dst.exists():os.link(src,dst)
items=[('pov',120,0,120,'pov-full.mp4',.5,.5),('pods',60,0,90,'source.mp4',.36,.5),('witness',75,180,255,'source.mp4',.64,.64),('corridor',93,255,348,'source.mp4',.45,.38),('scanner',137,0,0,'',.5,.5),('hologram',175,540,730,'source.mp4',.5,.5),('windup',60,730,780,'source.mp4',.5,.4),('shatter',60,780,807,'source.mp4',.4,.26),('emerge',36,807,829,'source.mp4',.3,.4),('escape',40,829,880,'source.mp4',.37,.28),('pursuit',60,880,954,'source.mp4',.48,.55),('title',56,0,0,'',.5,.5)]
f=0;segments=[]
for id,d,a,b,file,x0,x1 in items:
 segments.append(dict(id=id,fromFrame=f,duration=d,sourceStart=a,sourceEnd=b,rate=(b-a)/d,file=file,x0=x0,x1=x1));f+=d
m={'composition':{'width':720,'height':1280,'fps':30,'durationInFrames':f},'segments':segments,'title':'SOBAYA HAZARD','music':{'file':'aura/revenge.wav','startFrame':0,'revealFrame':485,'shatterFrame':720,'endFrame':972,'beatFrames':[485,502,516,532,547,561,576,590,605,620,634,651,662,720,748,759,770,781,792,804,815,833,847,867,889,900,917,931,945,960]},'originalAudio':False,'dialogueCaptions':False,'output':'final_remotion_sobaya_hazard_aura_9x16.mp4','notes':'No repeated source-video ranges. Full generated POV replaces previous 3-second close-up; unused original pod establishment restored. Side-by-side English scanner; vertical subject tracking. Music cadence proposal from waveform, not subjective audition.'}
assert f==972
(r/'src/aura-hazard.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(f)
