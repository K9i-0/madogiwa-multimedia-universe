from pathlib import Path
import json
r=Path(__file__).resolve().parent
m=json.loads((r/'src/aura-hazard-synced.json').read_text())
cuts=[0,30,55,81,127,215,374,388,449,500,552,597,634]
for i,s in enumerate(m['segments']):
 s['fromFrame']=cuts[i];s['duration']=cuts[i+1]-cuts[i]
 if s['id']=='pov':s['sourceEnd']=30
 if s['id']=='pods':s['sourceEnd']=25
 if s['id']=='witness':s['sourceEnd']=206
 if s['id']=='corridor':s['sourceEnd']=301
 if s['id']=='windup':s['freezeLeadFrames']=6
 s['rate']=(s['sourceEnd']-s['sourceStart'])/s['duration']
m['composition']['durationInFrames']=634
m['music'].update(startSample=532608,sampleRate=48000,startSeconds=11.096,startFrame=None,revealFrame=215,shatterFrame=388,endFrame=634,fadeOutStartFrame=610,fadeOutDurationFrames=24,beatFrames=[round((t-11.096)*30) for t in [11.88,12.34,12.84,13.35,14.44,14.82,15.27,15.67,16.16,16.72,17.21,17.73,18.23,18.71,19.21,19.65,20.17,20.66,21.12,21.7,22.06,24.01,24.36,24.93,25.3,25.68,26.05,26.41,26.81,27.18,27.75,28.22,28.89,29.62,30.01,30.56,31.02,31.51,32.0]])
m['scannerTiming']={'yameStart':0,'yameEnd':14,'fukuStart':17,'fukuEnd':41,'retrievalFrame':60}
m['output']='final_remotion_sobaya_hazard_reference_9x16.mp4'
m['reference']={'url':'https://youtube.com/shorts/B1loqFJymmY','durationSeconds':21.121,'musicOffsetSeconds':11.096,'audioCorrelationOpening':.981,'audioCorrelationAction':.993,'majorCutSeconds':[1,1.816667,2.7,4.233333,7.15,12.483333,12.933333,14.983333],'method':'Normalized waveform cross-correlation against original REVENGE; reference scene-cut detection and 0.1s action frames.'}
m['music'].pop('measuredAttackSeconds',None)
m['notes']='User requests copying reference music start and timing. Exact audio start11.096s, approximately same21.12s duration, major early cuts and12.933s action hit copied to 30fps nearest frames. Vertical shots, English scanner and SOBAYA HAZARD title retained. No source dialogue.'
(r/'src/aura-hazard-reference.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
s=(r/'src/aura-hazard-synced.tsx').read_text().replace('aura-hazard-synced.json','aura-hazard-reference.json').replace('SobayaHazardSynced','SobayaHazardReference').replace("s.id==='windup'&&f<20","s.id==='windup'&&f<6").replace("s.id==='windup'?734","s.id==='windup'?748")
(r/'src/aura-hazard-reference.tsx').write_text(s)
s=(r/'render-hazard-synced.mjs').read_text().replace('aura-hazard-synced','aura-hazard-reference').replace('out/hazard-synced','out/hazard-reference').replace('SobayaHazardSynced','SobayaHazardReference').replace('m.music.startFrame/m.composition.fps','m.music.startSample/m.music.sampleRate').replace('[0,110,172,390,391,408,409,435,476,637,724,725,726,755,783,830,900,961,980,1010]','[0,30,55,81,150,190,240,360,387,388,400,460,525,570,620]')
(r/'render-hazard-reference.mjs').write_text(s)
