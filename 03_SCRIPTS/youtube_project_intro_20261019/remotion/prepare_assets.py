from pathlib import Path
import os,json,subprocess,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'03_SCRIPTS';T=S/'youtube_members_explainer_20261013/remotion/public';records=[]
def link(src,name):
 src=Path(src);dst=P/'public'/name
 if not dst.exists():os.link(src,dst)
 records.append(dict(file=name,source=str(src.relative_to(R)),sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
for who in ['zunda','metan']:
 for f in T.glob(who+'_*.png'):link(f,f.name)
for name in ['main.wav','chair.png','takosan.png','sobaya.jpg','fukugyun.jpg','tokun.jpg','yotan.jpg','yametaro.jpg','okayaman.jpg','yumemin.jpg']:link(T/name,name)
for n in [1,2,3,4]:link(R/f'01_WORLD/story_timeline/episode_{n:02}.png',f'manga{n}.png')
vids={'commute.mp4':'63_madogiwa_super_try_commute/final_remotion_cm.mp4','proxy.mp4':'53_sobaya_proxy_worker_news/final_remotion_news.mp4','space.mp4':'64_madogiwa_super_try_space/final_remotion_cm.mp4','runway.mp4':'78_madogiwa_tshirt_runway/final_remotion_runway.mp4','coexist.mp4':'58_sobaya_takosan_fukuchan_mimic_chain/final_remotion_mimic_chain.mp4','workflow.mp4':'youtube_ai_video_workflow_20261013/final_remotion_ai_video_workflow_v12.mp4','tripo.mp4':'youtube_3d_character_workflow_20261014/final_remotion_tripo_workflow_v6.mp4','stickers_tutorial.mp4':'youtube_line_stickers_20261015/final_remotion_line_stickers_v8.mp4'}
for dst,src in vids.items():link(S/src,dst)
link(S/'31_debug_prayer_news/scene_02b_gyungyun_pose_start_production.png','prayer.png')
link(R/'16_MADOGIWA_STUDIO/public/site/goods/madogiwa-tshirt.webp','tshirt.webp')
link(R/'16_MADOGIWA_STUDIO/public/site/goods/madogiwa-line-stickers-preview.png','stickers.png')
link(R/'25_SOBAYA_IPPAI/qa/pouring.png','ippai.png')
link(S/'00_TEMPLATES/characters/character_sobaya_basic_sheet.png','reference.png')
link(R/'14_MADOGIWA_CARD_GAME/design/card_concepts/sobaya/sobaya-card-d-editorial-titanium.png','card_design.png')
# Short silent opening montage: climb → arrival → beer. No speed change.
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'public/commute.mp4'),'-filter_complex','[0:v]trim=0:5,setpts=PTS-STARTPTS[a];[0:v]trim=12:16,setpts=PTS-STARTPTS[b];[0:v]trim=21:26,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]','-map','[v]','-an','-c:v','libx264','-crf','18',str(P/'public/commute_intro.mp4')],check=True)
# Deterministic animated sticker playback as a video.
subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'27_LINE_STICKERS/sets/01/all-members-white-preview.gif'),'-vf','scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=30','-an','-c:v','libx264','-pix_fmt','yuv420p',str(P/'public/stickers.mp4')],check=True)
for name,sec in [('workflow',95),('tripo',80),('stickers_tutorial',95),('runway',10),('proxy',8),('space',8)]:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(sec),'-i',str(P/'public'/f'{name}.mp4'),'-frames:v','1',str(P/'public'/f'{name}.jpg')],check=True)
(P.parent/'asset_sources.json').write_text(json.dumps(dict(assets=records,openingCutsSeconds=[[0,5],[12,16],[21,26]],websiteCapturedAt='2026-10-19',portraitSourceRecord='03_SCRIPTS/youtube_explainer_pilot_20261008/asset_sources.json',music='ほのぼのワルツ【リコーダー】／エクシエ',musicSource='https://commons.nicovideo.jp/works/nc116360'),ensure_ascii=False,indent=2))
