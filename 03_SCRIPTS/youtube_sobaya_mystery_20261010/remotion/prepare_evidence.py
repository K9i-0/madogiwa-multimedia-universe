from pathlib import Path
import subprocess,json,hashlib,shutil
P=Path(__file__).resolve().parent;root=P.parents[2]
sources={'tribe':root/'03_SCRIPTS/74_yhk_jungle_available/final_remotion_documentary.mp4','space':root/'03_SCRIPTS/64_madogiwa_super_try_space/wan3_result_seed640030_480p.mp4','clone':root/'03_SCRIPTS/80_sobaya_clone_lab/final_remotion_clone_lab_skin.mp4','capture':root/'03_SCRIPTS/84_madogiwa_tribe_origin/final_remotion_story.mp4'}
# Source video crops remove burned-in titles, subtitles, HUD labels and broadcaster bugs.
# Reframing/low bandwidth/blur/grain form deliberately unreliable fictional evidence.
clips=[('witness','capture',26,7,'crop=iw*0.76:ih*0.64:iw*0.12:ih*0.12',True),('gate','tribe',26,7,'crop=iw*0.75:ih*0.65:iw*0.08:ih*0.1',False),('ritual','tribe',86,7,'crop=iw*0.78:ih*0.68:iw*0.06:ih*0.1',False),('amber','tribe',50,6,'crop=iw*0.8:ih*0.68:iw*0.1:ih*0.08',True),('ruins','clone',17,2,'crop=iw*0.43:ih*0.43:0:ih*0.08',False),('hologram','clone',21,5,'crop=iw*0.7:ih*0.66:iw*0.1:ih*0.06',False),('awakening','clone',28,4,'crop=iw*0.8:ih*0.66:iw*0.1:ih*0.12',True),('orbital','space',14,6,'crop=iw*0.66:ih*0.57:iw*0.26:ih*0.2',False),('gift','space',20,4,'crop=iw*0.72:ih*0.65:iw*0.16:ih*0.13',False)]
records=[]
for name,key,start,duration,crop,handheld in clips:
 target=P/'public'/f'evidence_{name}.mp4'
 # Filters apply only to the presentation derivative. No original is modified.
 vf=crop+',fps=15,scale=256:144,format=yuv420p,eq=brightness=-0.08:contrast=1.3:saturation=0,gblur=sigma=1.25,noise=alls=20:allf=t+u,scale=768:432:flags=neighbor'
 if name in ['witness','hologram','awakening','amber']:vf=vf.replace('scale=256:144','scale=128:72').replace('gblur=sigma=1.25','gblur=sigma=1.8')
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(sources[key]),'-t',str(duration),'-an','-vf',vf,'-c:v','libx264','-crf','24','-preset','fast',str(target)],check=True)
 still=P/'public'/f'evidence_{name}.jpg'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(0 if name=='gate' else min(2,duration/2)),'-i',str(target),'-frames:v','1',str(still)],check=True)
 records.append({'asset':target.name,'source':str(sources[key].relative_to(root)),'sourceSeconds':start,'durationSeconds':duration,'filter':vf,'additionalRendering':'handheld jitter, occlusion, frame drop and scanlines in Evidence.tsx' if handheld else 'fixed observation camera, scanlines and dropouts in Evidence.tsx','sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
shutil.copy2(P.parent/'inputs/sobaya_silhouette_v2.png',P/'public/sobaya_silhouette_v2.png')
(P.parent/'evidence_sources_v2.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
