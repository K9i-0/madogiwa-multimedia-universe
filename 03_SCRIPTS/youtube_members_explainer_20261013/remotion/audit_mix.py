from pathlib import Path
import json,subprocess,numpy as np,wave
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text())
with wave.open(str(P/'public/mixed.wav')) as w: sr=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(np.float32)/32768
report={'sampleRate':sr,'samples':len(a),'duration':len(a)/sr,'peakDBFS':float(20*np.log10(np.max(np.abs(a)))),'clippedSamples':int(np.sum(np.abs(a)>=.999)),'voiceSegments':[],'clips':[]}
for label,events in [('voiceSegments',m['dialogue']),('clips',m['clips'])]:
 for d in events:
  x=a[d['startFrame']*1600:(d['startFrame']+d['durationInFrames'])*1600];rms=float(np.sqrt(np.mean(x*x)));report[label].append({'id':d['id'],'rmsDBFS':float(20*np.log10(max(1e-9,rms))),'peakDBFS':float(20*np.log10(max(1e-9,np.max(np.abs(x)))))});assert rms>.003,(label,d['id'])
assert len(a)==m['composition']['durationInFrames']*1600;assert report['clippedSamples']==0
(P.parent/'qa_audio_levels.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('peak',report['peakDBFS'],'voice RMS range',min(x['rmsDBFS'] for x in report['voiceSegments']),max(x['rmsDBFS'] for x in report['voiceSegments']))
