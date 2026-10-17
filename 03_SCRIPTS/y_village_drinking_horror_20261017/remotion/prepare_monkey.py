"""Prepare a licensed real howler recording, without pitch or speed changes."""
from pathlib import Path
import subprocess, json, hashlib, urllib.request
P=Path(__file__).resolve().parent;R=P.parents[2]
source=R/'.local/y-village-horror/audio_sources/howler_monkey.ogg'
url='https://upload.wikimedia.org/wikipedia/commons/b/b8/Howler_monkey.ogg'
if not source.exists():
 source.parent.mkdir(parents=True,exist_ok=True)
 source.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MadogiwaVideoEditor/1.0'})).read())
target=P/'public/sfx/howler_monkey_v5.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-af','atrim=start=4:end=14,asetpts=PTS-STARTPTS,highpass=f=100,lowpass=f=6500,afade=t=in:d=0.15,afade=t=out:st=9.4:d=0.6','-ar','24000','-ac','1',str(target)],check=True)
record={'title':'Howler monkey','author':"David O'Hara",'source':'https://commons.wikimedia.org/wiki/File:Howler_monkey.ogg','download':url,'license':'CC BY 3.0','licenseURL':'https://creativecommons.org/licenses/by/3.0/','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'adoptedFile':'remotion/public/sfx/howler_monkey_v5.wav','edits':'4–14 s excerpt; 100–6500 Hz filter; fades; 24 kHz mono; mix gain; unchanged pitch and speed','outputSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'use':'real jungle monkey cries over the three characters imitating monkeys; not claimed to have been recorded in Y village'}
(P.parent/'monkey-audio-source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(record)
