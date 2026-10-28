"""Preserve the approved DVD picture; add black padding and independent captions."""
from pathlib import Path
import hashlib,json,re,subprocess

EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
M=json.loads((EP/'remotion/src/edit-manifest.json').read_text())
FPS=M['composition']['fps']
SOURCE=EP/'final_remotion_mega_dvd.mp4'
OUTPUT=EP/'final_remotion_shorts_9x16_v1.mp4'
if OUTPUT.exists():raise FileExistsError('Keep published previews; choose a new version filename for revisions.')
colors=(ROOT/'03_SCRIPTS/00_TEMPLATES/subtitles/member-colors.ts').read_text()
def color(name):
 h=re.search(rf"{name}: '#([0-9A-Fa-f]{{6}})'",colors).group(1)
 return '&H00'+h[4:6]+h[2:4]+h[0:2]
# Dialogue times use the existing scene evidence; no new recognition or voice generation.
scene=next(s['start'] for s in M['segments'] if s['id']=='scene')
captions=[
 {'start':scene+17,'end':scene+114,'speaker':'福ギュン','style':'Fukugyun','text':'そば屋さんには、\nこちらをご用意しました。'},
 {'start':scene+114,'end':scene+183,'speaker':'そば屋','style':'Sobaya','text':'なんで、僕だけ\nこんなに大きいんですか。'},
]
texts=[
 '窓際社員には、\nメガジョッキで\nビールを提供しましょう。',
 '通常のジョッキでは、\nすぐに飲み干されて\nしまいます。',
 None,
 '職場に続いて\n酒席でも干すのは、\n重ねて失礼に当たります。',
 '相手のお立場に配慮し、\nメガジョッキを\nご用意しましょう。',
 '一般社員には\n通常のジョッキ。',
 '窓際社員には、\nメガジョッキ。',
 'この違いが、\nできる社会人の気配りです。',
]
for i,c in enumerate(M['captions']):
 if i==2:
  split=c['start']+round((c['end']-c['start'])*.4)
  captions.extend([
   {'start':c['start'],'end':split,'style':'Narrator','text':'ビールを飲み干す\nという行為は、'},
   {'start':split,'end':c['end'],'style':'Narrator','text':'職場で人を干す行為を\n連想させてしまいますね。'},
  ])
 else:captions.append({'start':c['start'],'end':c['end'],'style':'Narrator','text':texts[i]})
for c in captions:assert 0<=c['start']<c['end']<=M['composition']['durationInFrames']
manifest={'version':'v1','source':SOURCE.name,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output':OUTPUT.name,'width':720,'height':1280,'fps':FPS,'durationInFrames':M['composition']['durationInFrames'],'picture':{'x':0,'y':370,'width':720,'height':540,'crop':False,'preserve_dvd_ui_and_captions':True},'background':'black','audio':'AAC stream copy from approved DVD master','captions':captions}
(EP/'shorts-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
def stamp(frame):
 cs=round(frame/FPS*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
'''
for name,size,outline in [('Fukugyun',38,color('fukuchan')),('Sobaya',38,color('sobaya')),('Narrator',38,'&H00202020'),('Name',28,'&H00000000')]:
 header+=f'Style: {name},Hiragino Sans,{size},&H00FFFFFF,&H00FFFFFF,{outline},&H00000000,0,0,0,0,100,100,0,0,1,{3 if name!="Name" else 0},0,8,40,40,0,1\n'
header+='\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
for c in captions:
 text=c['text'].replace('\n',r'\N')
 header+=f'Dialogue: 0,{stamp(c["start"])},{stamp(c["end"])},{c["style"]},,0,0,0,,{{\\an8\\pos(350,1000)}}{text}\n'
 if 'speaker' in c:header+=f'Dialogue: 0,{stamp(c["start"])},{stamp(c["end"])},Name,,0,0,0,,{{\\an8\\pos(350,953)}}{c["speaker"]}\n'
(EP/'shorts-captions.ass').write_text(header)
subprocess.run(['ffmpeg','-y','-v','warning','-i',SOURCE.name,'-map','0:v:0','-map','0:a:0','-vf','scale=720:540:flags=lanczos,pad=720:1280:0:370:black,setsar=1,ass=shorts-captions.ass','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',OUTPUT.name],cwd=EP,check=True)
print(str(OUTPUT),flush=True)
