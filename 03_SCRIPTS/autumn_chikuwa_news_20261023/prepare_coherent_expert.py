"""Offline edit: one approved introduction take; existing visible speech and explanation."""
from pathlib import Path
import json,subprocess,re,math,hashlib,shutil
P=Path(__file__).resolve().parent;O=P/'remotion/out/coherent_expert_20261024'
def run(a):return subprocess.run(list(map(str,a)),capture_output=True,text=True,check=True)
def duration(p):return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]).stdout)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=O/'anchor_intro.wav'
levels=json.loads(re.findall(r'\{[^{}]+\}',run(['ffmpeg','-hide_banner','-i',raw,'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr)[-1])
gain=min(-18-float(levels['input_i']),-1.5-float(levels['input_tp']))
target=P/'voice_anchor_expert_intro.wav'
run(['ffmpeg','-y','-v','error','-i',raw,'-af',f'volume={gain}dB','-ar','48000','-ac','1','-c:a','pcm_s16le',target])
# "はい" ends before .306s; measured silence .306–.979. Start .8s keeps .179s pre-roll.
run(['ffmpeg','-y','-v','error','-i',P/'voice_expert_beer.wav','-af','atrim=start=0.8,asetpts=PTS-STARTPTS','-c:a','pcm_s16le',P/'voice_expert_beer_continuation.wav'])
m=json.loads((O/'previous_manifest.json').read_text());s=m['final'];seq=[];at=0
for old in s['sequences']:
 r=dict(old)
 if r['id']=='bridge_expert':r['duration']=12+math.ceil(duration(target)*30)+6
 if r['id']=='comparison':r['duration']=math.ceil(duration(P/'voice_expert_beer_continuation.wav')*30)+6
 r['from']=at;at+=r['duration'];seq.append(r)
 if r['id']=='bridge_expert':seq.append({'id':'expert','duration':81,'from':at});at+=81
s['sequences']=seq;s['composition']['durationInFrames']=at
s['beerExplanation']['beerClueFrom']=224-24
# Final six seconds of the introduction show the existing silent listening clip.
intro=next(r for r in seq if r['id']=='bridge_expert')
s['coherentExpert']={'generatedTakes':1,'listeningFrom':max(12,intro['duration']-180),'continuationTrimSamples':38400}
(P/'remotion/src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
record=dict(generationAttempts=1,newVideoGenerationRequests=0,newImageGenerationRequests=0,model='Aratako/Irodori-TTS-v4-Large',seed=2026,reference='voice_forest.wav',referenceSha256=sha(P/'voice_forest.wav'),text='旬を迎えた天然のちくわですが、採る際には注意も必要です。ちくわ生物学が専門の、窓際大学のおかやまん准教授に伺います。',caption='落ち着いた地方局ニュース読み。標準語で、明瞭かつ均一な速度、抑制された抑揚で真面目に話す。',cfg=5,durationScale=1,uncut=True,rawSha256=sha(raw),adoptedSha256=sha(target),seconds=duration(target),gainDb=gain,expertOriginal='wan3_expert_480p.mp4 frames 27..108, original audio and video',expertContinuation='voice_expert_beer.wav samples 38400..end; no resynthesis or speed change',compositionFrames=at)
(P/'coherent_expert_20261024.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
for f in [target,P/'voice_expert_beer_continuation.wav']:shutil.copy2(f,P/'remotion/public'/f.name)
print(json.dumps(record,ensure_ascii=False,indent=2))
