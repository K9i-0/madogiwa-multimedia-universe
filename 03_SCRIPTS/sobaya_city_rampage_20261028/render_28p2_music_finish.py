#!/usr/bin/env python3
"""28.2s ending: shift music excerpt to source 27.8–56, fade after last accent."""
from pathlib import Path
import json,subprocess
P=Path(__file__).resolve().parent
FPS=30;FRAMES=846;DURATION=FRAMES/FPS
prior=json.loads((P/'edit_manifest_v8b.json').read_text())
master=P/'generated/mix_master_28p2_music_finish.wav'
filters=(f"[0:a]aresample=48000,atrim=end_sample={FRAMES*1600},asetpts=PTS-STARTPTS,volume={prior['sfx_gain_db']}dB,afade=t=in:st=7.8:d={2/FPS},afade=t=out:st=27.9:d=0.3:curve=hsin[sfx];"
 f"[1:a]atrim=start_sample=86400:end_sample=1440000,asetpts=PTS-STARTPTS,volume={prior['bgm_gain_db']}dB,afade=t=in:d=0.015,afade=t=out:st=27.6:d=0.6:curve=hsin[bgm];"
 '[sfx][bgm]amix=inputs=2:duration=longest:normalize=0,atrim=duration=28.2,alimiter=limit=0.891251:level=0:latency=1[mix]')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(P/'generated/assembled_v8b_lossless.mkv'),'-i',str(P/'local_audio/bgm_26_56_stereo.wav'),'-filter_complex',filters,'-map','[mix]','-c:a','pcm_s24le','-ar','48000','-ac','2','-y',str(master)],check=True)
out=P/'final_sobaya_brewery_28p2_music_finish_720p.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(P/'preview_sobaya_brewery_drink_start_28p2s_720p.mp4'),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t','28.2','-movflags','+faststart','-y',str(out)],check=True)
(P/'edit_manifest_28p2_music_finish.json').write_text(json.dumps({'output':out.name,'duration':DURATION,'fps':FPS,'frames':FRAMES,'music_source_in':27.8,'music_source_out':56,'music_shift_seconds':1.8,'last_accent_proposal':27.54,'music_fade_out_start_frame':828,'music_fade_out_frames':18,'sfx_fade_out_start_frame':837,'sfx_fade_out_frames':9,'fade_curve':'hsin','sfx_timing':'unchanged','video':'stream copy of approved 28.2s preview','note':'Music shifted globally; previous music/action alignments change by 1.8 seconds. Last accent is waveform-derived cue, not a verified beat-grid marker.','filter_complex':filters},ensure_ascii=False,indent=2)+'\n')
print('READY: '+str(out),flush=True)
