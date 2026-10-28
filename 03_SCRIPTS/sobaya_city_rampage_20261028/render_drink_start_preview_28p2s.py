#!/usr/bin/env python3
"""Alternate ending: stop just as drinking begins; retain accepted 30s version."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
frames=846;fps=30;duration=frames/fps;fade_frames=4
out=P/'preview_sobaya_brewery_drink_start_28p2s_720p.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(P/'generated/assembled_v8b_lossless.mkv'),'-i',str(P/'generated/mix_master_v8b.wav'),'-filter_complex',f'[0:v]trim=end_frame={frames},setpts=PTS-STARTPTS[v];[1:a]atrim=end_sample={frames*1600},asetpts=PTS-STARTPTS,afade=t=out:st={(frames-fade_frames)/fps}:d={fade_frames/fps}[a]','-map','[v]','-map','[a]','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-y',str(out)],check=True)
(P/'edit_manifest_drink_start_preview_28p2s.json').write_text(json.dumps({'source':'v8b','output':out.name,'fps':fps,'end_frame_exclusive':frames,'duration':duration,'audio_fade_out_frames':fade_frames,'video_fade':False,'purpose':'User-requested comparison ending at start of drink; accepted 30s version retained.'},ensure_ascii=False,indent=2)+'\n')
print('READY: '+str(out),flush=True)
