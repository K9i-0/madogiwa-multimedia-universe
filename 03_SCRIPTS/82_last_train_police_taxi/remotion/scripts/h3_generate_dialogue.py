from pathlib import Path
import sys,json,time,hashlib,subprocess
root=Path.cwd();sys.path.insert(0,str(root/'.local/Irodori-TTS-large'))
from irodori_tts.inference_runtime import InferenceRuntime,RuntimeKey,SamplingRequest,download_hf_checkpoint,save_wav
out=root/'.local/h3-episode82-edit'; model='Aratako/Irodori-TTS-v4-Large'
lines=[('01','yametaro','そろそろ終電やで。',''),('02','sobaya','あと一杯だけ！','明るく軽い調子で誘う。'),('03','fukuchan','かんぱーい！','楽しそうに乾杯する。'),('04','yametaro','せやから言うたやん。',''),('05','fukuchan','あ、タクシー！','車を見つけて嬉しそうに呼びかける。'),('06','sobaya','止めます。','落ち着いてさらっと言う。'),('07','yametaro','止め方！','驚いて鋭くツッコむ。'),('08','fukuchan','赤坂までお願いします。','相手へ明るく丁寧に頼む。'),('09','fukuchan','あ、そこのコンビニ寄ってもらっていいですか？','相手へ気軽に頼む自然な会話。'),('10','yametaro','タクシーちゃうねん。','')]
voices={'yametaro':('Yametaro_voice.wav',7),'sobaya':('Sobaya_voice.wav',42),'fukuchan':('Fukuchan_voice.wav',100)}
rt=InferenceRuntime.from_key(RuntimeKey(checkpoint=download_hf_checkpoint(model),model_device='mps',codec_device='mps'))
rows=[]
for idx,speaker,text,caption in lines:
 ref,seed=voices[speaker];path=out/f'{idx}_{speaker}_raw.wav'
 opts=dict(text=text,caption=caption or None,ref_wav=str(root/'02_CHARACTERS'/ref),seed=seed,trim_tail=False,cfg_scale_text=5.0 if speaker=='yametaro' else 3.0,duration_scale=0.70 if speaker=='yametaro' and not caption else 1.0)
 if path.exists():raise RuntimeError(f'Refusing to regenerate existing {path}')
 print('START',idx,text,flush=True);start=time.time()
 result=rt.synthesize(SamplingRequest(**opts),log_fn=print);save_wav(path,result.audio,result.sample_rate)
 final=out/f'{idx}_{speaker}.wav'
 if speaker=='sobaya':subprocess.run([str(root/'tools/sobaya_monsterize.sh'),str(path),str(final)],check=True)
 else:final.write_bytes(path.read_bytes())
 rows.append(dict(id=idx,speaker=speaker,text=text,model=model,settings=opts,ref_sha256=hashlib.sha256(Path(opts['ref_wav']).read_bytes()).hexdigest(),path=str(final.relative_to(root)),raw_duration=result.audio.shape[-1]/result.sample_rate,sha256=hashlib.sha256(final.read_bytes()).hexdigest(),elapsed_seconds=time.time()-start,postprocess='sobaya_monsterize' if speaker=='sobaya' else 'none'))
 (out/'generation.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print('DONE',idx,rows[-1]['raw_duration'],flush=True)
