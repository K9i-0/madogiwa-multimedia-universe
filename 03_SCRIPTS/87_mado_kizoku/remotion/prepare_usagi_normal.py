"""Rebuild v11 adopted mix with only Takosan replaced; preserve previous files."""
from pathlib import Path
import hashlib,json,subprocess,wave,os
import numpy as np
import urllib.request
P=Path(__file__).resolve().parent;E=P.parent;S=48000;N=1162*1600
O=P/'public/usagi-normal';O.mkdir(parents=True,exist_ok=True)
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def save(p,a):
 with wave.open(str(p),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(S);w.writeframes(np.clip(np.rint(a*32768),-32768,32767).astype('<i2').tobytes())
wav=E/'part2_takosan_usagi_normal.wav'
if not wav.exists():
 q=json.loads((E/'usagi_query.json').read_text())
 req=urllib.request.Request('http://127.0.0.1:50021/synthesis?speaker=61',data=json.dumps(q).encode(),headers={'Content-Type':'application/json'})
 wav.write_bytes(urllib.request.urlopen(req,timeout=120).read())
part1=pcm(P/'public/part1_audio.wav');v=pcm(E/'part1_fukugyun_seedvc.wav');part1[180*1600:284*1600]=v
part2=pcm(P/'public/audio_notifications.wav');old=pcm(P/'public/repaired_audio.wav');part2[580*1600:663*1600]-=old[580*1600:663*1600]
usagi=pcm(E/'part2_takosan_usagi_normal.wav');usagi*=.85/max(float(np.abs(usagi).max()),1e-8)
assert len(usagi)<=83*1600
original=part2.copy();prior=pcm(E/'part2_takosan_voicevox.wav');original[580*1600:580*1600+len(prior)]+=prior
part2[580*1600:580*1600+len(usagi)]+=usagi
assert np.array_equal(part2[:580*1600],original[:580*1600]) and np.array_equal(part2[663*1600:],original[663*1600:])
a=np.zeros((N,2),np.float32)
a[:len(part1)]+=part1
start=427*1600;a[start:start+len(part2)]+=part2
bgm=pcm(P/'public/bgm_mix.wav');a[:len(bgm)]+=bgm
assert np.max(np.abs(a))<1
save(O/'mix.wav',a)
src=E/'final_remotion_subtitles_v11_seedvc.mp4';dst=O/'adopted_v11.mp4'
if not dst.exists():os.link(src,dst)
record={'source':src.name,'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':'final_remotion_subtitles_v12_usagi_normal.mp4','frames':1162,'fps':30,'width':1280,'height':720,'takosan':{'engine':'VOICEVOX','style':61,'name':'中国うさぎ・ノーマル','speedScale':1.1,'pitchScale':0,'text':'本番もお燃えになってますわ。','startFrame':1007,'durationSeconds':len(usagi)/S,'peakTarget':.85,'input':'part2_takosan_usagi_normal.wav','sha256':hashlib.sha256((E/'part2_takosan_usagi_normal.wav').read_bytes()).hexdigest()},'otherPart2PCMUnchanged':True,'peak':float(np.abs(a).max()),'creditStartFrame':1102,'subjectiveListening':'unavailable','lipSync':'Existing Wan mouth shapes retained; not phoneme-synchronized to new voice.'}
(E/'usagi_normal_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False))
