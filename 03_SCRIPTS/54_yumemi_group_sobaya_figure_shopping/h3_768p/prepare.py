"""Prepare authorized 1344x768 two-part R2V test; original audio and canonical photos."""
from pathlib import Path
import json,hashlib,subprocess,sys,shutil,zipfile
P=Path(__file__).resolve().parent;EP=P.parent;ROOT=EP.parents[1];S=ROOT/'.claude/skills/minimax-h3-video/scripts'
job=Path(sys.argv[1]).resolve();job.mkdir(parents=True,exist_ok=False);B=job/'bundle';B.mkdir()
files={
'intro.png':P/'scene_intro.png','comparison.png':P/'scene_comparison.png',
'figure.png':EP/'sobaya_figure_wan_reference.png','fukugyun.jpg':ROOT/'02_CHARACTERS/Fukuchan.jpg',
'fukugyun_sheet.png':ROOT/'03_SCRIPTS/00_TEMPLATES/characters/character_fukuchan_basic_sheet.png',
'tokun.jpg':ROOT/'02_CHARACTERS/Tokun.jpg','tokun_sheet.png':EP/'character_tokun_basic_sheet.png',
'sobaya.jpg':ROOT/'02_CHARACTERS/Sobaya.jpg','sobaya_sheet.png':ROOT/'03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png'}
for n,p in files.items():shutil.copy2(p,B/n)
audios=[f'line{i:02}_'+('fukuchan' if i<6 else 'sobaya')+'.wav' for i in range(1,7)]
for n in audios:shutil.copy2(EP/n,B/n)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(EP/audios[-1]),'-af','apad=whole_dur=2','-t','2',str(B/'line06_sobaya_pad.wav')],check=True)
images=[['intro.png','figure.png','fukugyun.jpg','fukugyun_sheet.png','tokun.jpg','tokun_sheet.png'],['comparison.png','intro.png','figure.png','fukugyun.jpg','fukugyun_sheet.png','tokun.jpg','tokun_sheet.png','sobaya.jpg','sobaya_sheet.png']]
common='''Photoreal Japanese television home-shopping parody. Modern high-definition camera, warm cream/gold/coral studio, natural proportions, sharp facial details. Images are references, never collages or labels in the output. Fukugyun is the exact real Japanese man in his reference photographs, black jacket, white graphic shirt, black trousers, white shoes. His skin quality and apparent age match the canonical close-ups: clean even cared-for complexion with subtle forehead/eye/smile wrinkles; do not add spots, freckles, rough pores, erase wrinkles, de-age or reshape face. Tokun is the exact real man from his photo, mint tropical shirt, straw hat, purple glasses, pink lei, dark trousers, ukulele. He is silent, mouth closed. The ONE product sculpture is an INERT rigid FRP object, not a person. Copy its crude round ball shoulders, thin legs, simple visible joints, low-poly hands, cheap painted mask, dark SHORTS, fake rigid beer mug and original low rectangular plinth exactly. Do NOT improve its anatomy or craftsmanship. It NEVER speaks, breathes, blinks, moves joints, or turns its head. Live actors and product are separate identities, never morph or exchange faces/clothes. No extra objects or duplicated people. No generated titles, prices, subtitles, logos, UI or background speech. All exact graphics added in editing. No music. Keep bottom 15 percent and top corners clear for graphics. Preserve faces throughout each camera move. Use the completed attached dialogue recordings as exact performances in the stated order, not merely voice style, no repetitions or added words. Stable human lip movements for Fukugyun, never animate the product mouth.'''
texts=[
'''Reference order: Picture1 is stage blocking; Picture2 is exact inert sculpture; Pictures3/4 are Fukugyun face and clothes; Pictures5/6 are Tokun face and clothes. ONLY two live people Fukugyun and Tokun plus one sculpture; live Sobaya does not appear yet.
0.0-1.8s: smooth short push toward the product, luxurious shopping introduction.
1.8-5.96s: Fukugyun gestures proudly to sculpture and says <d>[Japanese] 本日ご紹介するのは、等身大そば屋フィギュア！</d> to <Audio 1>. Medium view with his mouth visible, correct face.
6.0-10.4s: detailed closeups of the sculpture's obviously crude shoulders and hands, Fukugyun offscreen says <d>[Japanese] 職人が細部まで仕上げた、驚きの再現度です！</d> to <Audio 2>. Keep original sculpture shape, do not beautify.
10.7-14.22s: return to Fukugyun and Tokun, Fukugyun asks <d>[Japanese] とーくん社長、こちら、おいくらですか？</d> to <Audio 3>. Tokun does not speak.
14.3-15.083s: Tokun solemnly nods and begins one ukulele strum near14.93s. No price text in video.''',
'''Reference order: Picture1 is final comparison layout; Picture2 is earlier studio with Tokun; Picture3 is the INERT sculpture; Pictures4/5 are Fukugyun; Pictures6/7 are Tokun; Pictures8/9 are LIVE Sobaya. Keep exact faces from original photos, not reinterpretations. LIVE Sobaya's rigid white mask from Picture8 is mandatory throughout; gray exposed skin including hands; huge muscular body, fitted white short-sleeve T-shirt, black LONG trousers, white sneakers, realistic beer mug. Preserve chest muscles and natural cloth folds but no nipple tips/outlines/spot shadows. His mask stays rigid; do not remove or deform it. Sculpture has SHORTS and skinny legs, not live Sobaya's anatomy.
0.0-1.8s: close shot of Tokun finishing his single ukulele gesture and solemn nod, mouth closed. Price will be overlaid by editor.
2.2-5.76s: Fukugyun says <d>[Japanese] そして、ご本人にも来ていただきました！</d> to <Audio 1>, live Sobaya steps into the comparison position beside the completely motionless sculpture. Show Fukugyun speaking with correct face.
6.1-9.54s: camera cuts to the clear full-body side-by-side composition of Picture1, Fukugyun offscreen enthusiastically says <d>[Japanese] うわ、どっちが本物かわからないぎゅん！</d> to <Audio 2>.
9.7-12.8s: awkward silence, hold the unmistakable contrast. The product is absolutely motionless. Only live Sobaya breathes, his mask remains rigid.
12.8-14.041s: LIVE Sobaya says <d>[Japanese] わかるやろ。</d> to <Audio 3>, subtly tilting his head. The sculpture does not react or speak. End with both full bodies and their feet visible.''']
chapters=[]
for i in range(2):
 name=f'ch{i+1:02}';used=audios[:3] if i==0 else audios[3:5]+['line06_sobaya_pad.wav'];prompt=common+'\n\n'+texts[i]
 (P/f'prompt_{name}.txt').write_text(prompt+'\n');(B/f'{name}.txt').write_text(prompt)
 args=[sys.executable,str(S/'build_workflow.py'),'--mode','r2v','--width','1344','--height','768','--frames','362','--steps','20','--seed',str(54076801+i),'--prefix','video/shopping768_'+name,'--prompt-file',str(B/f'{name}.txt'),'--out',str(B/f'{name}.json')]
 for f in images[i]:args+=['--image',f]
 for f in used:args+=['--audio',f]
 subprocess.run(args,check=True)
 chapters.append(dict(id=name,frames=362,width=1344,height=768,seed=54076801+i,images=images[i],audio=used,ref_image_size='match'))
(B/'chapter_plan.json').write_text(json.dumps(chapters,indent=2));(P/'chapter_plan.json').write_text(json.dumps(chapters,indent=2)+'\n')
for n in ['setup_cuda.py','run_workflow.py']:shutil.copy2(S/n,B/n)
shutil.copy2(P/'colab_batch.py',B/'colab_remote.py')
manifest=[dict(file=n,source=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for n,p in files.items()]
manifest += [dict(file=n,source=str((EP/n).relative_to(ROOT)),sha256=hashlib.sha256((EP/n).read_bytes()).hexdigest()) for n in audios]
(P/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in B.iterdir():z.write(p,p.name)
(job/'job.json').write_text(json.dumps(dict(status='prepared',bundle_sha256=hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest()),indent=2))
print('Ready',job)
