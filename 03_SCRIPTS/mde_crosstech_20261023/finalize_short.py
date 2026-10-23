"""Mux the approved master audio cut onto the vertical Remotion render."""
from pathlib import Path
import subprocess,json,hashlib
p=Path(__file__).resolve().parent
m=json.loads((p/'remotion/src/shorts-manifest.json').read_text())
d=m['contentFrames']/m['fps'];total=m['durationInFrames']/m['fps']
source=p/'final_remotion_mde_v2_16x9.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(p/'remotion/out/short-silent.mp4'),'-i',str(source),'-filter_complex',f"[1:a]atrim=start_sample={m['sourceStart']*1600}:end_sample={m['sourceEnd']*1600},asetpts=PTS-STARTPTS,afade=t=out:st={d-.3}:d=0.3,apad=pad_dur=2,atrim=duration={total}[a]",'-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(p/'final_remotion_shorts_9x16.mp4')],check=True)
meta=json.loads((p/'youtube_metadata.json').read_text())
meta['snippet']['title']='AIが迫る「エクセル操作してるフリ」の終焉｜新人罪MDEとは？ #Shorts'
meta['snippet']['description']='AI時代、仕事をしているフリは通用するのか。新人罪MDEをご紹介。\n\n本編：https://www.youtube.com/watch?v=TRf4LlHUNrc\n公式サイト：https://madogiwa.work/\n\n音声：Irodori-TTS（そば屋／ゆめテレアナウンサー）\n映像：窓際族物語「プロフェッショナル 窓際の流儀」\n静止画：OpenAI Imagegen\n音楽：本作オリジナルの電子音楽\n\nMDE、Accidenchua、窓際クロステックは架空設定です。'
(p/'shorts_youtube_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
