from pathlib import Path
import json,subprocess
r=Path(__file__).resolve().parent
m=json.loads((r/'src/aura-hazard.json').read_text())
# Integer frame cuts nearest measured low-frequency attacks in the requested music excerpt.
cuts=[0,111,173,270,363,476,697,725,783,830,900,961,1020]
for i,s in enumerate(m['segments']):
 s['fromFrame']=cuts[i];s['duration']=cuts[i+1]-cuts[i];s['rate']=(s['sourceEnd']-s['sourceStart'])/s['duration']
byid={s['id']:s for s in m['segments']}
byid['hologram']['sourceEnd']=754
byid['windup'].update(sourceStart=754,sourceEnd=762,freezeLeadFrames=20)
byid['shatter']['sourceStart']=762
byid['windup']['x1']=.46
byid['shatter']['x0']=.46
for shot in m['segments']: shot['rate']=(shot['sourceEnd']-shot['sourceStart'])/shot['duration']
subprocess.run(['ffmpeg','-v','error','-ss',str(754/30),'-i',str(r/'public/aura/source.mp4'),'-frames:v','1','-y',str(r/'public/aura/pre-impact.jpg')],check=True)
peaks=[22.06,23.815,24.14,24.545,24.9,25.3,25.685,26.025,26.385,26.75,27.11,27.755,28.13,28.465,28.795,29.19,29.525,29.855,30.2,30.62,30.99,31.39,31.76,32.13,32.73,33.085,33.625,34.085,34.71,35.035,35.64,36.04,36.505,36.87,37.21,37.875,38.275,38.82,39.19,39.56,39.935,40.335,40.835,41.22,41.83,42.235,42.735,43.225,43.755,44.165,44.655,45.24,45.715,46.16,46.845,47.17,47.66,48.09,48.64,49.085,49.66,50.075,50.61,50.98,51.33,51.67,51.995,52.51,52.97,53.53,54.02,54.51,55.02,55.51]
m['composition']['durationInFrames']=1020
m['music'].update(startFrame=660,revealFrame=476,shatterFrame=725,endFrame=1020,beatFrames=sorted(set(round((t-22)*30) for t in peaks)),measuredAttackSeconds=peaks,fadeOutStartFrame=1002,fadeOutDurationFrames=18)
m['scannerTiming']={'yameStart':0,'yameEnd':28,'fukuStart':28,'fukuEnd':46,'retrievalFrame':72}
m['output']='final_remotion_sobaya_hazard_bgm22_synced_9x16.mp4'
m['notes']='Music 22.0–56.0 seconds. All shot cuts and effect pulses rebuilt against measured low-frequency attack frames. No repeated primary video ranges. Ending lands on title at music54.02s, with final phrase ending into music56s energy drop.'
(r/'src/aura-hazard-synced.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
s=(r/'src/aura-hazard.tsx').read_text().replace("'./aura-hazard.json'","'./aura-hazard-synced.json'").replace('SobayaHazardAura','SobayaHazardSynced')
s=s.replace('f>=24','f>=m.scannerTiming.yameEnd').replace('start:0,end:24','start:m.scannerTiming.yameStart,end:m.scannerTiming.yameEnd').replace('start:35,end:66','start:m.scannerTiming.fukuStart,end:m.scannerTiming.fukuEnd').replace('f>=110','f>=m.scannerTiming.retrievalFrame')
s=s.replace('g>=720','g>=m.music.shatterFrame').replace('f>=720&&f<726?1-(f-720)/6:0','f>=m.music.shatterFrame&&f<m.music.shatterFrame+6?1-(f-m.music.shatterFrame)/6:0').replace('const sh=f-720','const sh=f-m.music.shatterFrame').replace('ease(f,961,971,0,1)','ease(f,m.composition.durationInFrames-12,m.composition.durationInFrames-1,0,1)')
s=s.replace("const video=(ghost=false)=><OffthreadVideo", "const video=(ghost=false)=>s.id==='windup'&&f<20?<Img src={staticFile('aura/pre-impact.jpg')} style={mediaStyle}/>:<OffthreadVideo").replace("startFrom={s.sourceStart-(ghost?2:0)} playbackRate={s.rate}","startFrom={s.id==='windup'?734:s.sourceStart-(ghost?2:0)} playbackRate={s.id==='windup'?1:s.rate}")
(r/'src/aura-hazard-synced.tsx').write_text(s)
s=(r/'render-hazard.mjs').read_text().replace('aura-hazard','aura-hazard-synced').replace('out/hazard-aura','out/hazard-synced').replace('SobayaHazardAura','SobayaHazardSynced').replace('[0,80,145,205,300,390,470,530,630,690,723,750,800,840,885,945]','[0,110,172,390,391,408,409,435,476,637,724,725,726,755,783,830,900,961,980,1010]')
s=s.replace("'volume=0.56,afade=t=in:d=0.15,afade=t=out:st=31.95:d=0.45,alimiter=limit=0.84:level=false:latency=true'","`atrim=start=${m.music.startFrame/m.composition.fps}:duration=${m.composition.durationInFrames/m.composition.fps},asetpts=PTS-STARTPTS,volume=0.48,afade=t=in:d=0.04,afade=t=out:st=${m.music.fadeOutStartFrame/m.composition.fps}:d=${m.music.fadeOutDurationFrames/m.composition.fps},alimiter=limit=0.8:level=false:latency=true`")
(r/'render-hazard-synced.mjs').write_text(s)
