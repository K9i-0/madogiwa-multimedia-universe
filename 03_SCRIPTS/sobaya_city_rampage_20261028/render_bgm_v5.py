#!/usr/bin/env python3
"""Mix the specified 26–56s music excerpt with generated effects; no video retiming."""
from pathlib import Path
import subprocess,json,math,re
BASE=Path(__file__).resolve().parent
SOURCE=BASE/'generated/assembled_v5_lossless.mkv'
MUSIC=BASE/'local_audio/bgm_26_56_stereo.wav'
WORK=BASE/'generated';WORK.mkdir(exist_ok=True)
def run(args):
 return subprocess.run(args,check=True,capture_output=True,text=True)
def probe(path):
 return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]).stdout)
def loudness(path):
 r=run(['ffmpeg','-hide_banner','-i',str(path),'-vn','-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'])
 return json.loads(re.findall(r'\{\s*"input_i"[\s\S]*?\}',r.stderr)[-1])
def gain(info,target):
 value=float(info['input_i']);return target-value if math.isfinite(value) else 0
if not SOURCE.exists():raise SystemExit('Generated source is not available yet.')
p=probe(SOURCE);vs=next(s for s in p['streams'] if s['codec_type']=='video')
duration=float(vs.get('duration',p['format']['duration']));fps=vs['avg_frame_rate']
mi=loudness(MUSIC);si=loudness(SOURCE)
mg=gain(mi,-16);sg=gain(si,-22)
master=WORK/'mix_master_v5.wav'
filters=f'[0:a]aresample=48000,volume={sg:.6f}dB[sfx];[1:a]aresample=48000,volume={mg:.6f}dB[bgm];[sfx][bgm]amix=inputs=2:duration=longest:normalize=0,atrim=duration={duration},afade=t=in:d=0.015,afade=t=out:st={max(0,duration-.08)}:d=0.08,alimiter=limit=0.891251:level=0:latency=1[mix]'
run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(SOURCE),'-i',str(MUSIC),'-filter_complex',filters,'-map','[mix]','-c:a','pcm_s24le','-ar','48000','-ac','2','-y',str(master)])
outputs=[]
for size in ['720p','480p']:
 out=BASE/f'final_sobaya_brewery_bgm_v5_{size}.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-i',str(SOURCE),'-i',str(master),'-map','0:v:0','-map','1:a:0']
 if size=='720p':cmd+=['-vf','scale=1280:720:flags=lanczos,setsar=1','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough']
 else:cmd+=['-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough']
 cmd+=['-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-t',str(duration),'-y',str(out)]
 run(cmd);outputs.append(out.name);print('READY: '+str(out),flush=True)
record={'source':SOURCE.name,'music':str(MUSIC.relative_to(BASE)),'music_source_in':26,'music_source_out':56,'duration':duration,'fps':fps,'video_retiming':False,'source_loudness':si,'music_loudness':mi,'sfx_gain_db':sg,'bgm_gain_db':mg,'mix_limiter_peak':-1,'mix_master':str(master.relative_to(BASE)),'resize':'source directly to 1280x720, Lanczos','outputs':outputs,'filter_complex':filters}
(BASE/'edit_manifest_v5.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Edit manifest saved.',flush=True)
