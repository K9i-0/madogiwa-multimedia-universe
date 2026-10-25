"""Re-edit adopted voices: silence-only trims, per-line pacing, mora-timed captions/cues."""
from pathlib import Path
import json,wave,math,sys,re,hashlib,requests
import numpy as np
P=Path(__file__).resolve().parent;R=P.parents[2]
sys.path.insert(0,str(R/'.claude/skills/voicevox-control/scripts'))
from prepare_readings import load_dictionary,prepare_row
from subtitle_layout import captions
D=load_dictionary(local_path=P/'readings.json')
# The v4 snapshot is derived from the adopted voice record, not a generated audio dependency.
rows=json.loads((P.parent/'voice_generation_record.json').read_text())
cue_words=['制約','サイズ','位置','ペイント','エンジン','頂点','バッファ','シェーダー','描画命令','ラスタライズ','フラグメント','Flutter Scene','Flutter GPU','Impeller','モデル','カメラ','ライト','アニメーション','端末の傾き','落下物','キャッチ','得点','スワイプ','ピンチ操作','斜め','Codex','Claude Code','Dart MCP','Marionette MCP','mobile MCP','Dart Tooling Daemon','Dart VM Service','Binding','Widget','文字','キー','タップ','構造化','乱数','一定時間','Android','iPhone','実機','profile','人が','30fps','60fps','4096','2048','1.9','0.74','福ギュン','そば屋','おだてつ','形','寸法','コードを直して','hot reload','結果を確かめる','次の修正','毎フレーム','上流','性能','画面で傾けた','原型','骨組み']
cache=P/'out/alignment_queries';cache.mkdir(exist_ok=True)
def prefix_moras(text,speaker):
 if not text:return []
 speech=prepare_row({'id':'align','text':text},D,scopes=['mmu','tech'])['speech']
 key=hashlib.sha256(f'{speaker}:{speech}'.encode()).hexdigest();path=cache/f'{key}.json'
 if path.exists():q=json.loads(path.read_text())
 else:
  r=requests.post('http://127.0.0.1:50021/audio_query',params={'speaker':speaker,'text':speech},timeout=60);r.raise_for_status();q=r.json();path.write_text(json.dumps(q,ensure_ascii=False))
 return [x['text'] for a in q['accent_phrases'] for x in a['moras']]
cursor=48;chapter=[];lastscene=None;decisions=[]
for i,d in enumerate(rows):
 q=json.loads((P/d['queryFile']).read_text())
 with wave.open(str(P.parent/d['audio'])) as w:rate=w.getframerate();samples=np.frombuffer(w.readframes(w.getnframes()),'<i2')/32768
 # Preserve at least 50/80ms surrounding all audible material; never cut syllables.
 idx=np.flatnonzero(abs(samples)>.003);trim=max(0,int(idx[0]-rate*.05));end=min(len(samples),int(idx[-1]+rate*.08))
 d['audioTrimStartSample']=trim;d['audioTrimEndSample']=end;d['audioSourceRate']=rate
 duration=math.ceil((end-trim)/rate*30);d['durationInFrames']=duration;d['startFrame']=cursor
 if lastscene!=d['scene']:chapter.append({'id':d['scene'],'startFrame':0 if not chapter else cursor});lastscene=d['scene']
 full=[];times=[];t=q['prePhonemeLength']/q['speedScale']
 for ap in q['accent_phrases']:
  for mo in ap['moras']:
   times.append(t);full.append(mo['text']);t+=((mo.get('consonant_length') or 0)+mo['vowel_length'])/q['speedScale']
  if ap.get('pause_mora'):t+=ap['pause_mora']['vowel_length']/q['speedScale']
 times.append(t)
 def at(char):
  if char<=0:return 0
  tokens=prefix_moras(d['text'][:char],d['speaker']);n=min(len(tokens),len(full))
  # Prefix analysis can alter the last word's reading; use the stable mora prefix.
  same=0
  for a,b in zip(tokens,full):
   if a!=b:break
   same+=1
  if n-same>5: # retain explicit evidence for rare contextual differences
   decisions.append({'id':d['id'],'alignmentPrefix':d['text'][:char],'matchedMoras':same,'prefixMoras':n})
  return max(0,min(duration-1,round((times[n]-trim/rate)*30)))
 pages=captions(d['text'],duration);char=0;starts=[]
 for c in pages:
  starts.append(at(char));char+=len(c['text'].replace('\n',''))
 for j,c in enumerate(pages):c['fromFrame']=starts[j];c['toFrame']=starts[j+1] if j+1<len(pages) else duration
 assert all(c['toFrame']>c['fromFrame'] for c in pages)
 d['captions']=pages;d['cues']={}
 for word in cue_words:
  if word in d['text']:d['cues'][word]=at(d['text'].index(word))
 s=samples[trim:end];d['envelope']=[round(float(np.sqrt(np.mean(s[int(j*rate/30):min(len(s),int((j+1)*rate/30))]**2))),4) for j in range(duration)]
 nxt=rows[i+1] if i+1<len(rows) else None
 gap=.34;reason='question_answer'
 if nxt and nxt['who']==d['who']:gap=.23;reason='continuation'
 if nxt and nxt['scene']!=d['scene']:gap=.78;reason='chapter_breath'
 if nxt and nxt['view']!=d['view'] and d['who']=='metan':gap=.48;reason='visual_change'
 if nxt and nxt['text'] in ['そんなものはないわ。','そうよね！','こっちもFlutterの話よ。']:gap=.19;reason='quick_reply'
 if d['text']=='そんなものはないわ。':gap=.72;reason='deadpan_hold'
 if d['text']=='そうよね！':gap=.68;reason='joke_to_topic'
 if d['view'] in ['stack','deterministic','memory'] and d['who']=='metan':gap=.65;reason='read_diagram'
 pad=max(0,round((gap-.13)*30));d['gapAfterFrames']=pad;d['pacingReason']=reason
 cursor+=duration+pad
 print(d['id'],round(cursor/30,1),flush=True)
comp={'width':1280,'height':720,'fps':30,'durationInFrames':cursor+75}
m={'composition':comp,'mainStartFrame':chapter[1]['startFrame'],'endingStartFrame':chapter[-1]['startFrame'],'voicevoxVersion':'0.25.1','chapters':chapter,'dialogue':rows,'clips':[],'editVersion':8}
(P/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(P/'edit_timing_v5.json').write_text(json.dumps({'method':'Original VOICEVOX moras; prefix readings identify caption/cue boundaries. Silence-only source trims. No speech time stretch.','decisions':decisions,'lines':[{k:d[k] for k in ['id','startFrame','durationInFrames','audioTrimStartSample','audioTrimEndSample','gapAfterFrames','pacingReason','cues']} for d in rows]},ensure_ascii=False,indent=2))
print('DURATION',cursor/30+2.5)
