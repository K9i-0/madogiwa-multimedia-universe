"""Build local review page, upload metadata and QA record for the five Shorts."""
import json,subprocess,hashlib,html,io
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent;repo=root.parents[1]
items=[('81_sobaya_yakumi_shopping','sobaya-fun-soba-making','そば屋の楽しいそば作り',8.7,'final_remotion_yakumi_call_crop.mp4'),('42_chikuwa_line_fishing_soba_shark','chikuwa-line-fishing-soba-shark','そばシャーク — 遭遇',26.7,'final_remotion_daichikuwa.mp4'),('63_madogiwa_super_try_commute','madogiwa-super-try-commute','窓際スーパーつらい — 出社インポッシブル篇',7.6,'final_remotion_cm.mp4'),('68_tako_game_dormitory','tako-game-dormitory','タコゲーム — 目覚め',21.9,'final_remotion_subtitles_v2.mp4'),('88_doku_chikuwa','detective-yotan-chikuwa-mystery','名探偵ヨータン 残されたちくわの謎',36.2,'studio_delivery_v23.mp4')]
plan=json.loads((root/'plan.json').read_text());rows=[];cards=[]
(root/'out').mkdir(exist_ok=True);(root/'metadata').mkdir(exist_ok=True)
def pcm(p):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vn','-f','s16le','-'])).hexdigest()
for order,(folder,slug,title,cover,audio) in enumerate(items,1):
 ep=repo/'03_SCRIPTS'/folder;p=ep/'final_remotion_shorts_9x16.mp4'
 if not p.exists():raise FileNotFoundError(p)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_read_frames,sample_rate:format=duration','-of','json',str(p)]))
 v=next(s for s in probe['streams'] if s['codec_type']=='video');assert (v['width'],v['height'])==(720,1280)
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
 before=pcm(ep/audio);after=pcm(p);assert before==after
 m=json.loads((ep/'remotion/src/shorts-manifest.json').read_text());assert int(v['nb_read_frames'])==m['composition']['durationInFrames']
 for c in m['captions']:assert 0<=c['startFrame']<c['endFrame']<=int(v['nb_read_frames'])
 # Source, subtitle boundaries, longest captions and ending in review contact sheets.
 times=sorted(set([.1,cover,float(probe['format']['duration'])-.15]+[(c['startFrame']+c['endFrame'])/60 for c in m['captions']]))
 cols=5;w=240;h=447;sheet=Image.new('RGB',(cols*w,((len(times)+cols-1)//cols)*h),'#111');d=ImageDraw.Draw(sheet)
 for k,t in enumerate(times):
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=240:427','-f','image2pipe','-vcodec','mjpeg','-']);im=Image.open(io.BytesIO(b));x=k%cols*w;y=k//cols*h;sheet.paste(im,(x,y));d.text((x+5,y+427),f'{t:.2f}s',fill='white')
 sheet.save(root/'out'/f'{order:02d}-audit.jpg',quality=88)
 thumb=root/'out'/f'{order:02d}-cover.jpg';subprocess.run(['ffmpeg','-v','error','-ss',str(cover),'-i',str(p),'-frames:v','1','-y',str(thumb)],check=True)
 original=next(x for x in plan['videos'] if x['slug']==slug)
 metadata={'snippet':{'title':title+' #Shorts','description':f'{title}\n\n窓際族物語の縦版ショート。\n横版：https://youtu.be/{original["youtube_id"]}\n\n#窓際族物語 #そば屋 #Shorts','categoryId':'23','tags':['窓際族物語','そば屋','Shorts']},'status':{'privacyStatus':'public','selfDeclaredMadeForKids':False}}
 (root/'metadata'/f'{order:02d}-{slug}.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
 rows.append({'order':order,'slug':slug,'title':title,'file':str(p.relative_to(repo)),'source_youtube_id':original['youtube_id'],'duration_seconds':float(probe['format']['duration']),'video_frames':int(v['nb_read_frames']),'resolution':[720,1280],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'audio_pcm_sha256':after,'audio_unchanged':True,'decode':'pass','caption_layout':'bottom_area','caption_timing_review':'existing timing or ASR-assisted; direct auditory review not performed','publication_status':'prepared_not_uploaded'})
 relative='../'+folder+'/final_remotion_shorts_9x16.mp4';cards.append(f'<article><h2>{order}. {html.escape(title)}</h2><video controls preload="metadata" poster="out/{order:02d}-cover.jpg" src="{relative}"></video><p><a href="{relative}">MP4を開く</a> · {float(probe["format"]["duration"]):.1f}秒</p></article>')
(root/'delivery.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(root/'review.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><title>Shorts 初回5本</title><style>body{background:#15191f;color:#eee;font:16px system-ui;margin:28px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}article{background:#222933;padding:16px;border-radius:14px}h2{font-size:18px;min-height:50px}video{width:100%;max-height:70vh;background:#000}a{color:#ffdc86}</style><h1>Shorts 初回5本</h1><p>投稿準備済み・未登録。タコゲームは既存字幕を下へ移設。</p><main>'+''.join(cards)+'</main><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(o=>{if(o!==v)o.pause()})))</script></html>')
print('Prepared and verified',len(rows),'videos; all audio PCM identical.')
