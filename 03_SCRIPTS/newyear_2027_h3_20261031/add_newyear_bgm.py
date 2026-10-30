"""Add licensed MMT38 Haru no Umi; retain video packets and earlier versions."""
from pathlib import Path
import json,subprocess,hashlib
EP=Path(__file__).resolve().parent
m=json.loads((EP/'remotion/src/edit-manifest.json').read_text());duration=m['composition']['durationInFrames']/24
music=EP/'generated/music/harunoumi_mmt38.mp3';master=EP/'generated/music/master_bgm_v3.wav'
# Music 1.5 dB above downloaded level under dialogue, +5 dB during the flashback.
fc=f"[0:a]volume=-1.5dB[d];[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,aresample=48000,volume='if(lt(t,13.5),1.19,if(lt(t,14.5),1.19+(t-13.5)*0.59,1.78))':eval=frame,afade=t=in:d=0.08,afade=t=out:st={duration-0.7}:d=0.7[b];[d][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=false:latency=true[out]"
subprocess.run(['ffmpeg','-y','-v','error','-i',str(EP/'remotion/public/master.wav'),'-i',str(music),'-filter_complex',fc,'-map','[out]','-ar','48000','-c:a','pcm_s24le',str(master)],check=True)
out=EP/'final_remotion_newyear_v3_harunoumi.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(EP/'final_remotion_newyear_v2.mp4'),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(out)],check=True)
record={'title':'春の海（琴・尺八）','composer':'宮城道雄','recording_artist':'MMT38','source_page':'https://mmt38.info/download/春の海フル/','terms':'https://mmt38.info/kiyaku/','checked_date':'2026-10-31','permission_summary':'Free commercial/noncommercial content use; optional credit; no redistribution as music material, no Content ID registration. Source audio kept locally under ignored generated/music/.','source_sha256':hashlib.sha256(music.read_bytes()).hexdigest(),'source_start_seconds':0,'used_seconds':duration,'filter_complex':fc,'output':out.name,'video':'stream copy of v2; unchanged visual frames','credit':'BGM：春の海（作曲：宮城道雄）／音源：MMT38 https://mmt38.info/'}
(EP/'music_sources.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(EP/'music-credit.txt').write_text('BGM：春の海（作曲：宮城道雄）\n音源：MMT38 / MMT STUDIO\nhttps://mmt38.info/\n\n音量調整・冒頭約21秒使用・末尾フェード。\n音源の素材再配布・Content ID登録はしない。\n')
print(out)
