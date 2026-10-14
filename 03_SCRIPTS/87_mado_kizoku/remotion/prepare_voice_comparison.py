"""Build v11 voice comparisons; preserve v10 and all PCM outside the two repairs.
Run from any directory with the Irodori environment's Python (numpy required).
Candidate synthesis and extraction commands: voice-comparison.md.
"""
from pathlib import Path
import hashlib, json, subprocess, wave
import numpy as np
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
W = ROOT / '.local/mado-kizoku-voice-v11'
OUT = P / 'public/voice-v11'
OUT.mkdir(parents=True, exist_ok=True)
SR = 48000

def pcm(path):
    data = subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar',str(SR),'-ac','2','-f','f32le','-'])
    return np.frombuffer(data, dtype='<f4').reshape(-1,2).copy()

def save(path, data):
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(np.clip(np.rint(data * 32768), -32768, 32767).astype('<i2').tobytes())

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def normalize(a): return a * (.85 / max(float(np.max(np.abs(a))), 1e-8))

base1 = pcm(P/'public/part1_audio.wav')
base2 = pcm(P/'public/audio_notifications.wav')
old2 = pcm(P/'public/repaired_audio.wav')
# Source video contains speech at 1.089..2.088 and 2.608..3.341 seconds.
# Seed-VC keeps the timeline; suppress only converted silent-room artifacts.
vc_path = next((W/'seedvc').glob('*.wav'))
vc = pcm(vc_path)
window = np.zeros((104*1600,2), dtype=np.float32)
window[:len(vc)] = vc
mask = np.zeros(len(window), dtype=np.float32)
for lo,hi in [(1.0,2.23),(2.50,104/30)]:
    a,b = round(lo*SR),round(hi*SR)
    mask[a:b] = 1
    fade = round(.015*SR)
    mask[a:a+fade] *= np.linspace(0,1,fade)
    # No terminal fade across the last syllable. The source's final padding is kept.
    if b < len(mask): mask[b-fade:b] *= np.linspace(1,0,fade)
window *= mask[:,None]
window = normalize(window)
save(OUT/'fukugyun_seedvc.wav',window)

# Independent TTS comparison: canonical voice but not source-aligned phonemes.
# No false claim of preserved internal pauses; only onset is aligned.
tts = normalize(pcm(W/'fukugyun_irodori_large.wav'))
tts_window = np.zeros_like(window)
start = round(1.089458*SR)
assert start+len(tts)<=len(tts_window)
tts_window[start:start+len(tts)] = tts
save(OUT/'fukugyun_irodori.wav',tts_window)

checks = {}
for variant,audio in [('seedvc',window),('irodori',tts_window)]:
    merged = base1.copy()
    a,b=180*1600,284*1600
    merged[a:b] = audio
    checks[variant+'_outside_repair_equal'] = bool(np.array_equal(merged[:a],base1[:a]) and np.array_equal(merged[b:],base1[b:]))
    save(OUT/f'part1_{variant}.wav',merged)

# Preserve all six existing notifications while removing only old Takosan speech.
a,b=580*1600,663*1600
new2=base2.copy()
new2[a:b] = base2[a:b]-old2[a:b]
tako=normalize(pcm(W/'takosan_voidoll.wav'))
assert len(tako)<b-a
new2[a:a+len(tako)] += tako
assert np.max(np.abs(new2))<1
checks['takosan_outside_repair_equal'] = bool(np.array_equal(new2[:a],base2[:a]) and np.array_equal(new2[b:],base2[b:]))
save(OUT/'part2_voidoll.wav',new2)
save(OUT/'takosan_voidoll.wav',tako)
record = {
 'status':'comparison; v10 retained; not a global voice-cast change',
 'sourceVideo':'wan3_fukuchan_closeup_480p.mp4',
 'upstream':{'repository':'https://github.com/sobaya-0141/Seedance_Madogiwa','revision':'af92df24b277a45450cda975b0549d4c6ee890e4'},
 'takosan':{'engine':'VOICEVOX','version':'0.25.1','speaker':'Voidoll','style':89,'speedScale':1.0,'text':'本番もお燃えになってますわ。','kana':'ホンバンモ / オモエニ / ナッテマスワ','startFrameInFull':1007,'seconds':len(tako)/SR,'credit':'VOICEVOX:Voidoll(CV:丹下桜)'},
 'fukugyun':{'target':'02_CHARACTERS/Fukuchan_voice.wav','targetSha256':sha(ROOT/'02_CHARACTERS/Fukuchan_voice.wav'),'sourceClipSeconds':[0,104/30], 'placementFramesInFull':[180,284], 'sourceSpeechIntervals':[[1.089458,2.087667],[2.608292,3.340667]],'seedvc':{'steps':50,'length_adjust':1.0,'cfg':.7,'f0_condition':True,'auto_f0_adjust':True,'fp16':False,'rawSeconds':len(vc)/SR,'timeStretch':False,'silenceArtifactGateSeconds':[[1.0,2.23],[2.50,104/30]],'warning':'Existing Seed-VC checkpoint loader reports skipped shape-mismatched keys; recorded in local log. Voice quality needs listening.'},'irodori':{'model':'Aratako/Irodori-TTS-v4-Large','seed':100,'cfg_text':5,'duration_scale':.7,'uncut':True,'text':'こちらのお菓子も、ギュンですわ。','rawSeconds':len(tts)/SR,'limitation':'Onset aligned only; TTS does not inherit source pause or phoneme timing.'}},
 'durationInFrames':1162,'fps':30,'width':1280,'height':720,
 'checks':checks,'listening':'Unavailable in this runtime; ASR, waveform and decoded frames inspected, not subjective approval.',
 'outputs':{p.name:{'sha256':sha(p)} for p in OUT.glob('*.wav')}
}
assert all(checks.values())
(P.parent/'voice_comparison_v11_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks)); print('Prepared',OUT)
