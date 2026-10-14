"""Derive readable captions and visual cues from the adopted v11 voice queries."""
from pathlib import Path
import json,re,urllib.request,urllib.parse
from PIL import ImageFont
P=Path(__file__).resolve().parent
m=json.loads((P/'src/edit-manifest.json').read_text())
font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',29)
replacements={'Claude Code':'クロードコード','Codex':'コーデックス','Remotion':'リモーション','Irodori':'イロドリ','Qwen Cloud':'クウェンクラウド','Wan 3.0':'ワン、サンテンゼロ','Wan':'ワン','API':'エーピーアイ','AI':'エーアイ','480p':'四百八十ピー','720p':'七百二十ピー','1080p':'千八十ピー','H3':'エイチスリー','TikTok':'ティックトック','ByteDance':'バイトダンス','Seedance':'シーダンス','Alibaba':'アリババ','MiniMax':'ミニマックス','Higgsfield':'ヒッグスフィールド','React':'リアクト','GitHub':'ギットハブ','Git':'ギット','GPU':'ジーピーユー','Colab':'コラボ','IT':'アイティー','100%':'ひゃくパーセント','福ギュン':'ふくぎゅん','Web':'ウェブ','〜':'。','動画生成の分です':'動画生成のぶんです','その分':'そのぶん','次の一本':'次のいっぽん','一本ずつ':'いっぽんずつ'}
def spoken(t):
 for a,b in replacements.items():t=t.replace(a,b)
 return t
cachefile=P/'out/v11_prefix_queries.json';cache=json.loads(cachefile.read_text()) if cachefile.exists() else {}
def mora_count(t):
 t=spoken(t)
 if t not in cache:
  url='http://127.0.0.1:50021/audio_query?'+urllib.parse.urlencode({'speaker':61,'text':t})
  q=json.load(urllib.request.urlopen(urllib.request.Request(url,data=b'',method='POST')))
  cache[t]=sum(len(p['moras']) for p in q['accent_phrases'])
 return cache[t]
def time_at(d,pos):
 if pos<=0:return 0
 if pos>=len(d['text']):return d['durationInFrames']
 q=d['voiceSettings'].get('query')
 if not q:return round(d['durationInFrames']*pos/len(d['text']))
 target=mora_count(d['text'][:pos]);sec=q['prePhonemeLength'];count=0
 for p in q['accent_phrases']:
  for z in p['moras']:
   if count>=target:return min(d['durationInFrames']-1,round(sec/q['speedScale']*30))
   sec+=z.get('consonant_length',0) or 0;sec+=z['vowel_length'];count+=1
  if p.get('pause_mora'):sec+=p['pause_mora']['vowel_length']
 return min(d['durationInFrames']-1,round(sec/q['speedScale']*30))
def wrap(t):
 if font.getlength(t)<=770:return t
 candidates=[]
 for i in range(1,len(t)):
  if t[i] in '、。！？）」』…' or t[i-1] in '「『（':continue
  if re.match(r'[A-Za-z0-9]',t[i-1]) and re.match(r'[A-Za-z0-9]',t[i]):continue
  widths=[font.getlength(t[:i]),font.getlength(t[i:])]
  if max(widths)>770:continue
  score=max(widths)+abs(widths[0]-widths[1])*.2-(1000 if t[i-1] in '。！？' else 800 if t[i-1] in '、' else 200 if t[i-1] in 'はがをにでとへもや' else 0)
  candidates.append((score,i))
 if not candidates:return None
 i=min(candidates)[1];return t[:i]+'\n'+t[i:]
def split(t):
 if wrap(t):return [t]
 # Prefer whole sentences, then punctuation; never shrink type to squeeze a paragraph.
 positions=[x.end() for x in re.finditer('[。！？、]',t) if x.end()<len(t)]
 choices=[i for i in positions if wrap(t[:i])]
 sentence_choices=[i for i in choices if t[i-1] in '。！？']
 i=max(sentence_choices or choices) if choices else max(i for i in range(1,len(t)) if wrap(t[:i]))
 return [t[:i]]+split(t[i:])
markers={16:['指示を','映像を','声を'],11:['作り方','かかるお金','失敗'],18:['Alibaba','MiniMax'],26:['音声'],67:['時間','動画に'],68:['映像の演技','正確な字幕'],78:['480p','720p','1080p'],82:['音声'],83:['画質'],100:['条件を'],92:['キャラクター','過去エピソード'],94:['次の制作','会話で'],102:['モデルを比較'],110:['Wan','必要な声','Remotion'],120:['480p','720p','1080p'],121:['平均300円'],122:['必要な部分']}
legacy={32:{'.28':'誰の体格','.58':'誰の仮面'},36:{'.53':'どの順','.75':'オチ'},47:{'.52':'全身'},51:{'.25':'今回','.55':'Wan'},58:{'.5':'必要な部分'},71:{'.24':'見出し'},74:{'.35':'顔や演技'},90:{'.45':'資料','.7':'実行コード'},98:{'.5':'合計時間'},100:{'.5':'全部の合計'},104:{'.5':'別の人'},105:{'.33':'どう直した','.65':'どこまで'}}
overrides=json.loads((P/"caption-layout-v11.json").read_text())
cues={}
for d in m['dialogue']:
 chunks=overrides.get(d['id'],split(d['text']));pos=0;segments=[]
 for t in chunks:
  start=time_at(d,pos);pos+=len(t.replace('\n',''));segments.append({'startFrame':start,'endFrame':time_at(d,pos),'text':t if '\n' in t else wrap(t)})
 assert ''.join(x['text'].replace('\n','') for x in segments)==d['text']
 assert all(x['endFrame']>x['startFrame'] for x in segments)
 d['captionSegments']=segments;d['caption']=segments[0]['text'];d['captionFontSize']=29
 n=int(d['id'][1:]);c={}
 for marker in markers.get(n,[]):c[marker]=time_at(d,d['text'].index(marker))
 for ratio,marker in legacy.get(n,{}).items():c[str(float(ratio))]=time_at(d,d['text'].index(marker))
 if c:cues[d['id']]=c
(P/'src/visual-cues-v11.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2)+'\n')
(P/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
cachefile.write_text(json.dumps(cache,ensure_ascii=False,indent=2))
print('Captions',sum(len(d['captionSegments']) for d in m['dialogue']),'Visual cue lines',len(cues))
