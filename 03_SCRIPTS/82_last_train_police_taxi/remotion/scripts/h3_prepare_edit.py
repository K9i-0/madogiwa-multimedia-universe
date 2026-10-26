from pathlib import Path
import json,subprocess,shutil,hashlib,math
root=Path.cwd();ep=root/'03_SCRIPTS/82_last_train_police_taxi';run=ep/'h3_20261026';rm=ep/'remotion';public=rm/'public/h3';public.mkdir(exist_ok=True)
for ch in (1,2):
 src=run/'generated'/f'ch{ch}_480p.mp4';dst=public/f'ch{ch}_480p.mp4'
 if not dst.exists():shutil.copy2(src,dst)
# Existing dialogue-free physical effects from the H3 source, not synthesized sounds.
fx=[('clink',90,121),('taxi_stop',231,281)]
for name,start,end in fx:
 path=public/f'{name}.wav'
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(public/'ch1_480p.mp4'),'-vn','-af',f'atrim=start={start/24}:end={end/24},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={(end-start)/24-0.05}:d=0.05','-ar','48000','-c:a','pcm_s16le',str(path)],check=True)
fxrecord={n:dict(source='h3_20261026/generated/ch1_480p.mp4',startFrame=s,endFrame=e,fps=24,sha256=hashlib.sha256((public/f'{n}.wav').read_bytes()).hexdigest()) for n,s,e in fx}
(rm/'h3-effects.json').write_text(json.dumps(fxrecord,indent=2)+'\n')
print('Inputs and effects prepared')
