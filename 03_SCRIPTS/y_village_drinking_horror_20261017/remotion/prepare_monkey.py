"""Prepare three CC0 human monkey imitations for a deliberately silly exchange."""
from pathlib import Path
import subprocess,json,hashlib,urllib.request
P=Path(__file__).resolve().parent;R=P.parents[2]
source_dir=R/'.local/y-village-horror/audio_sources'
source_dir.mkdir(parents=True,exist_ok=True)
sources=[]
for sound_id,role,title in [(588623,'y','Monkey noise (imitation)'),(588624,'m','Monkey noise (imitation) 2'),(588625,'n','Monkey noise (imitation) 3')]:
 url=f'https://cdn.freesound.org/previews/588/{sound_id}_5661246-hq.mp3'
 source=source_dir/f'freesound_{sound_id}.mp3'
 if not source.exists():
  source.write_bytes(urllib.request.urlopen(url,timeout=45).read())
 target=P/'public/sfx'/f'monkey_call_{role}_v7.wav'
 # Preserve three distinct performances without changing pitch or speed.
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-af','highpass=f=110,lowpass=f=7500,afade=t=in:d=0.02','-ar','24000','-ac','1',str(target)],check=True)
 sources.append({'title':title,'author':'wilika2','source':f'https://freesound.org/people/wilika2/sounds/{sound_id}/','download':url,'license':'CC0 1.0','licenseURL':'https://creativecommons.org/publicdomain/zero/1.0/','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'adoptedFile':str(target.relative_to(P.parent)),'edits':'Full performance; 110–7500 Hz filtering, onset fade, 24 kHz mono. Native pitch and speed. Mix applies short fades, gentle stereo position and gain.','outputSha256':hashlib.sha256(target.read_bytes()).hexdigest()})
record={'version':7,'sources':sources,'reference':{'url':'https://youtu.be/41NGxtJgNlM','title':'【フリーな音響素材】ジャングルの動物の鳴き声 Jungle Animal Sounds 3 Sound Effect','uploader':'音楽素材.net','descriptionLink':'http://xn--9qv61c515a0jz.net/videoblocks/','sameTitleCatalog':'https://www.storyblocks.com/audio/stock/jungle-animal-sounds-3-rxegaht2lpbk0wxxue9','status':'Reference only; no license for reuse verified. The final edit uses the CC0 sources above, not this video audio.'},'use':'Three distinct human monkey imitations, timed to Y, M and the narrator; no claim of a real animal recording.'}
(P.parent/'monkey-audio-source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(sources),'CC0 monkey imitations')
