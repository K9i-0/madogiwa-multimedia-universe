"""Reproduce adopted settings into local candidates; never overwrite adopted WAVs.
Run from repository root with the local Irodori Large Python environment.
"""
from pathlib import Path
import sys,json,subprocess
root=Path.cwd();sys.path.insert(0,str(root/'.local/Irodori-TTS-large'))
from irodori_tts.inference_runtime import InferenceRuntime,RuntimeKey,SamplingRequest,download_hf_checkpoint,save_wav
manifest=root/'03_SCRIPTS/82_last_train_police_taxi/remotion/h3-voice-manifest.json'
rows=json.loads(manifest.read_text());out=root/'.local/h3-episode82-reproduced';out.mkdir(parents=True,exist_ok=True)
if any(out.glob('*.wav')):raise RuntimeError('Output contains existing WAVs; preserve them before rerunning.')
rt=InferenceRuntime.from_key(RuntimeKey(checkpoint=download_hf_checkpoint(rows[0]['model']),model_device='mps',codec_device='mps'))
for row in rows:
 opts=dict(row['settings']);opts['ref_wav']=str(root/opts['ref_wav'])
 raw=out/f"{row['id']}_raw.wav";final=out/Path(row['path']).name
 result=rt.synthesize(SamplingRequest(**opts),log_fn=print);save_wav(raw,result.audio,result.sample_rate)
 if row['postprocess']=='sobaya_monsterize':subprocess.run([str(root/'tools/sobaya_monsterize.sh'),str(raw),str(final)],check=True)
 elif row['postprocess']=='trim':subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af',row['edit_filter'],str(final)],check=True)
 else:final.write_bytes(raw.read_bytes())
 print(final,flush=True)
