from pathlib import Path
import subprocess,json
p=Path(__file__).resolve().parent
source=p/'generated/assembled_v8b_lossless.mkv'
out=p/'final_sobaya_full_ending_30s_16x9.mp4'
af='aresample=48000,atrim=end_sample=1440000,asetpts=PTS-STARTPTS,volume=-8.13dB,alimiter=limit=0.891251:level=0:latency=1'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-map','0:v:0','-map','0:a:0','-frames:v','900','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-af',af,'-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(out)],check=True)
(p/'edit_manifest_full_ending.json').write_text(json.dumps({'source':str(source.relative_to(p)),'output':out.name,'frames':900,'fps':30,'duration':30,'audio_filter':af,'added_bgm':False,'restored_frames':[846,900],'ending':'Full generated drinking shot retained, no end fade or time adjustment. Existing flyby edit retained.','publication':'Files only; user will publish tomorrow.'},indent=2)+'\n')
print(out)
