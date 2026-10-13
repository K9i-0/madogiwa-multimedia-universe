from pathlib import Path
import json,subprocess,hashlib,argparse
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source',default='../final_remotion_ai_video_workflow_v3.mp4');parser.add_argument('--tag',default='v3');args=parser.parse_args()
src=(P/args.source).resolve();m=json.loads((P/'src/edit-manifest.json').read_text())
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(src)]));v=next(s for s in r['streams'] if s['codec_type']=='video');a=next(s for s in r['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1');assert int(v['nb_read_frames'])==m['composition']['durationInFrames'];assert a['sample_rate']=='48000';assert a['channels']==2
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
assert v.get('sample_aspect_ratio','1:1')=='1:1';assert a['codec_name']=='aac'
assert abs(float(a['duration'])-m['composition']['durationInFrames']/30)<.1
subprocess.run(['ffmpeg','-v','error','-i',str(src),'-f','null','-'],check=True)
res=subprocess.run(['ffmpeg','-hide_banner','-i',str(src),'-af','loudnorm=I=-18:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);stats=json.JSONDecoder().raw_decode(res.stderr[res.stderr.rfind('{'):])[0];(P/'out/final_loudness.json').write_text(json.dumps(stats,indent=2));assert float(stats['input_tp'])<0
report={'file':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'bytes':src.stat().st_size,'durationSeconds':m['composition']['durationInFrames']/30,'video':{'codec':v['codec_name'],'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'pixelFormat':v['pix_fmt'],'sampleAspectRatio':v.get('sample_aspect_ratio'),'frames':v['nb_read_frames']},'audio':{'codec':a['codec_name'],'sampleRate':48000,'channels':2,'integratedLUFS':stats['input_i'],'truePeakDbTP':stats['input_tp'],'loudnessRangeLU':stats['input_lra']},'fullDecode':'pass','subtitleTimingAndWidth':'See remotion/out/timeline_validation.json','visualReview':f'See review_{args.tag}.md and remotion/out/audit_{args.tag}*','audioReview':'Irodori canonical voice references and automated ASR; subjective continuous listening is not available in this tool environment.','newPaidVideoGeneration':False,'published':False}
(P.parent/f'delivery_{args.tag}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
