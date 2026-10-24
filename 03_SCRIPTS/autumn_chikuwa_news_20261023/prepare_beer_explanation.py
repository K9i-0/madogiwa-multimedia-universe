"""Offline adoption of the three approved dialogue takes. No generation or retries."""
from pathlib import Path
import hashlib,json,math,re,shutil,subprocess
P=Path(__file__).resolve().parent
OUT=P/'remotion/out/beer_explanation_20261024'
PUBLIC=P/'remotion/public'
def run(a):return subprocess.run(list(map(str,a)),check=True,capture_output=True,text=True)
def duration(f):return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]).stdout)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
anchor='落ち着いた地方局ニュース読み。標準語で、明瞭かつ均一な速度、抑制された抑揚で真面目に話す。'
lines=[
 ('anchor_question','voice_anchor_question.wav','旬を迎えた天然のちくわですが、採る際には注意も必要なんですよね。','voice_forest.wav',2026,anchor),
 ('expert_explanation','voice_expert_beer.wav','はい。山には毒ちくわも自生しています。見た目だけでは食用と区別がつきません。毒ちくわ特有のビール臭が、見分ける手がかりになります。','voice_ref_okayaman_visible.wav',42,''),
 ('anchor_response','voice_anchor_comparison_reply.wav','こうして並べてみても、見た目ではまったく違いが分かりませんね。では、もう一度、現場に戻ります。','voice_forest.wav',2026,anchor),
]
assert all((OUT/f'{k}.wav').exists() for k,*_ in lines)
records=[]
for key,name,text,ref,seed,caption in lines:
 raw=OUT/f'{key}.wav'
 source=raw
 # The final anchor take has a measured silent gap at 4.340–5.288s.
 # Remove only frames 135–149 of this gap, preserving every spoken sample.
 if key=='anchor_response':
  source=OUT/'anchor_response_gap_edit.wav'
  run(['ffmpeg','-y','-v','error','-i',raw,'-filter_complex','[0:a]atrim=end=4.5,asetpts=PTS-STARTPTS[a];[0:a]atrim=start=4.966666667,asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[out]','-map','[out]','-c:a','pcm_s16le',source])
 analysis=run(['ffmpeg','-hide_banner','-i',source,'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
 levels=json.loads(re.findall(r'\{[^{}]+\}',analysis)[-1]);gain=min(-18-float(levels['input_i']),-1.5-float(levels['input_tp']))
 target=P/name
 run(['ffmpeg','-y','-v','error','-i',source,'-af',f'volume={gain:.4f}dB','-ar','48000','-ac','1','-c:a','pcm_s16le',target])
 shutil.copy2(target,PUBLIC/name)
 records.append(dict(key=key,file=name,text=text,reference=ref,referenceSha256=sha(P/ref),seed=seed,caption=caption,
  model='Aratako/Irodori-TTS-v4-Large',textCfg=5,durationScale=1,uncut=True,generationAttempts=1,
  rawSha256=sha(raw),sha256=sha(target),seconds=duration(target),frames=math.ceil(duration(target)*30),gainDb=gain,speedChange=False,
  removedSilenceFramesAt30fps=[135,149] if key=='anchor_response' else None))
bykey={r['key']:r for r in records}
m=json.loads((OUT/'previous_manifest.json').read_text());spec=m['final'];cue=spec['feedback']['studioCueFrames']
spec['beerExplanation']={'generatedTakes':3,'beerClueFrom':224,'fieldStudioFrom':132}
seq=[];at=0
for old in spec['sequences']:
 if old['id']=='expert':continue
 s=dict(old)
 if s['id']=='bridge_expert':s['duration']=cue+bykey['anchor_question']['frames']+6
 if s['id']=='comparison':s['duration']=bykey['expert_explanation']['frames']+6
 if s['id']=='bridge_field':s['duration']=bykey['anchor_response']['frames']+6
 s['from']=at;at+=s['duration'];seq.append(s)
spec['sequences']=seq;spec['composition']['durationInFrames']=at
(P/'remotion/src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
record=dict(authorization='Approved three-line news exchange about wild poisonous chikuwa and beer odor.',
 generationAttempts=3,videoGenerationRequests=0,imageGenerationRequests=0,voices=records,
 setting='山に自生する毒ちくわは独特のビール臭がする。そば屋が食いつく伏線。',
 compositionFrames=at,compositionSeconds=at/30,listeningAudit='Not claimed; ASR and frame inspection are separate.')
(P/'beer_explanation_20261024.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False,indent=2))
