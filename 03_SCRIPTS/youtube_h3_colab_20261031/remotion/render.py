from pathlib import Path
import subprocess,sys,json
P=Path(__file__).resolve().parent
revision=json.loads((P/'src/edit-manifest.json').read_text())['revision']
output=P.parent/f'final_remotion_h3_colab_{revision}.mp4'
if output.exists():raise FileExistsError(f'Preserve delivered output; choose a new revision: {output}')
if '--no-mix' not in sys.argv:subprocess.run([sys.executable,str(P/'mix_audio.py')],check=True)
subprocess.run(['npx','remotion','render','src/index.ts','H3Colab',f'out/visuals_{revision}.mp4','--muted','--concurrency=6','--crf=20','--log=info'],cwd=P,check=True)
subprocess.run(['ffmpeg','-v','error','-n','-i',str(P/f'out/visuals_{revision}.mp4'),'-i',str(P/'public/mixed.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(output)],check=True)
print(output,flush=True)
