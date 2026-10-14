"""Restore adopted v11 mixes from tracked dialogue WAVs after base preparation."""
from pathlib import Path
import subprocess,wave
import numpy as np
P=Path(__file__).resolve().parent
O=P/'public/voice-v11';O.mkdir(exist_ok=True)
def pcm(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ar','48000','-ac','2','-f','f32le','-']),dtype='<f4').reshape(-1,2).copy()
def save(f,a):
 with wave.open(str(f),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(np.clip(np.rint(a*32768),-32768,32767).astype('<i2').tobytes())
a=pcm(P/'public/part1_audio.wav');v=pcm(P.parent/'part1_fukugyun_seedvc.wav')
assert len(v)==104*1600
a[180*1600:284*1600]=v;save(O/'part1_seedvc.wav',a)
a=pcm(P/'public/audio_notifications.wav');old=pcm(P/'public/repaired_audio.wav');v=pcm(P.parent/'part2_takosan_voicevox.wav')
assert len(v)<=83*1600
a[580*1600:663*1600]-=old[580*1600:663*1600];a[580*1600:580*1600+len(v)]+=v
assert np.abs(a).max()<1
save(O/'part2_voidoll.wav',a)
