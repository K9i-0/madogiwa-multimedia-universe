"""Assemble native H3 clips, without time stretch; subtitle timing follows audio audit."""
from pathlib import Path
import json,subprocess,shutil
EP=Path(__file__).resolve().parent
chapters=json.loads((EP/'chapter_plan.json').read_text())
out=EP/'remotion/public';out.mkdir(parents=True,exist_ok=True)
segments=[];start=0
for c in chapters:
 name=c['id']+'_480p.mp4'
 source=EP/'generated/h3-v1/results'/name
 if not source.exists():source=EP/'generated/partials'/name
 if not source.exists():raise FileNotFoundError(source)
 shutil.copy2(source,out/name)
 segments.append(dict(id=c['id'],file=name,startFrame=start,durationInFrames=c['frames'],trimStartFrame=0))
 start+=c['frames']
manifest=dict(composition=dict(width=1280,height=720,fps=24,durationInFrames=start),segments=segments,captions=[])
dest=EP/'remotion/src/edit-manifest.json'
if dest.exists():manifest['captions']=json.loads(dest.read_text()).get('captions',[])
dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
args=['ffmpeg','-y','-v','error']
for s in segments:args+=['-i',str(out/s['file'])]
filters=[]
for i,s in enumerate(segments):filters.append(f'[{i}:a]aresample=48000,atrim=duration={s["durationInFrames"]/24},asetpts=PTS-STARTPTS[a{i}]')
filters.append(''.join(f'[a{i}]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=0:a=1,afade=t=out:st={start/24-.5}:d=0.5[master]')
subprocess.run(args+['-filter_complex',';'.join(filters),'-map','[master]','-c:a','pcm_s16le',str(out/'master.wav')],check=True)
listing=EP/'generated/concat.txt'
listing.write_text(''.join("file '"+str(out/s['file'])+"'\n" for s in segments))
preview=EP/'preview_all_720p_v1.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-vf','scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(preview)],check=True)
print('PLAYABLE',preview,flush=True)
