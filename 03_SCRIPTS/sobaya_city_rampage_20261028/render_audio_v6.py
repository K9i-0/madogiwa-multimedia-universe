#!/usr/bin/env python3
"""Mute generated soundtrack through frame 234, retain music and bit-exact v5 video."""
from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
old=json.loads((P/'edit_manifest_v5.json').read_text())
# 234/30 seconds; restore generated effects over two frames after the sprint cut.
start=234/30;fade=2/30
master=P/'generated/mix_master_v6.wav'
filters=(f"[0:a]aresample=48000,volume={old['sfx_gain_db']:.6f}dB,afade=t=in:st={start}:d={fade}[sfx];"
 f"[1:a]aresample=48000,volume={old['bgm_gain_db']:.6f}dB[bgm];"
 '[sfx][bgm]amix=inputs=2:duration=longest:normalize=0,atrim=duration=30,afade=t=in:d=0.015,afade=t=out:st=29.92:d=0.08,alimiter=limit=0.891251:level=0:latency=1[mix]')
def run(args):subprocess.run(args,check=True)
run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(P/'generated/assembled_v5_lossless.mkv'),'-i',str(P/'local_audio/bgm_26_56_stereo.wav'),'-filter_complex',filters,'-map','[mix]','-c:a','pcm_s24le','-ar','48000','-ac','2','-y',str(master)])
outputs=[]
for size in ['720p','480p']:
 out=P/f'final_sobaya_brewery_bgm_v6_{size}.mp4'
 run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(P/f'final_sobaya_brewery_bgm_v5_{size}.mp4'),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t','30','-movflags','+faststart','-y',str(out)])
 outputs.append(out.name);print('READY: '+str(out),flush=True)
record={'base':'v5','fps':30,'total_frames':900,'generated_audio_muted_frames':[0,234],'generated_audio_fade_in_frames':2,'music_source_in':26,'music_source_out':56,'sfx_gain_db':old['sfx_gain_db'],'bgm_gain_db':old['bgm_gain_db'],'video':'stream copy, no re-encoding','outputs':outputs,'filter_complex':filters,'tradeoff':'Opening generated ambience/effects also removed; no source separation or additional generation.'}
(P/'edit_manifest_v6.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
