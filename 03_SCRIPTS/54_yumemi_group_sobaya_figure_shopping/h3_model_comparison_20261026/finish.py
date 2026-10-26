"""Produce unobstructed 30s comparisons. Quality is deliberately left to the user."""
from pathlib import Path
import json,subprocess,sys
P=Path(__file__).resolve().parent;EP=P.parent;ROOT=P.parents[2]
results=Path(sys.argv[1]).resolve()
master=EP/'remotion/public/shopping_irodori_instrumental_master_30s.wav'
variants={
 'pure': [ROOT/'.local/h3-shopping-768-20261026/job/results'/f'ch{i:02}_768p.mp4' for i in [1,2]],
 'singularity_v2': [results/f'singularity_v2_ch{i:02}.mp4' for i in [1,2]],
 'hybrid_b20': [results/f'hybrid_b20_ch{i:02}.mp4' for i in [1,2]]}
def run(args):subprocess.run(args,check=True)
reports=[]
for name,clips in variants.items():
 raw=EP/f'h3_compare_raw_{name}.mp4';out=EP/f'final_h3_compare_{name}.mp4'
 filt='[0:v]trim=end_frame=360,setpts=PTS-STARTPTS[v0];[1:v]trim=end_frame=360,setpts=PTS-STARTPTS[v1];[0:a]atrim=end=15,asetpts=PTS-STARTPTS[a0];[1:a]atrim=end=15,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
 run(['ffmpeg','-v','error','-y','-i',str(clips[0]),'-i',str(clips[1]),'-filter_complex',filt,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-t','30','-movflags','+faststart',str(raw)])
 run(['ffmpeg','-v','error','-y','-i',str(raw),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','30','-movflags','+faststart',str(out)])
 for f in [raw,out]:
  d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(f)]));v=next(x for x in d['streams'] if x['codec_type']=='video')
  assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1344,768,'24/1',720)
  run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'])
  reports.append({'file':f.name,'resolution':[1344,768],'frames':720,'fps':24,'seconds':30,'decode':'passed'})
outputs=[EP/f'final_h3_compare_{x}.mp4' for x in variants]
args=['ffmpeg','-v','error','-y']
for f in outputs:args+=['-i',str(f)]
font='/System/Library/Fonts/Helvetica.ttc'
labels=['Pure Ref2VA','Singularity V2','Hybrid b20-49']
filters=[]
for i,label in enumerate(labels):filters.append(f"[{i}:v]scale=672:384:flags=lanczos,pad=672:432:0:48:black,drawtext=fontfile='{font}':text='{label}':fontsize=26:fontcolor=white:x=(w-tw)/2:y=10[v{i}]")
filters.append('[v0][v1][v2]hstack=inputs=3[v]')
run(args+['-filter_complex',';'.join(filters),'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','fast','-crf','18','-c:a','copy','-t','30','-movflags','+faststart',str(EP/'final_h3_compare_side_by_side.mp4')])
remote=json.loads((results/'status.json').read_text());baseline=json.loads((EP/'h3_768p/generation-result.json').read_text())
report={'qualityReview':'User judges; no rerolls or quality selection','baselineReused':True,'baseline':baseline,'newRun':remote,'outputs':reports,'audioPolicy':'final_* uses identical adopted Irodori master; h3_compare_raw_* retains native generated audio; no captions, crops, speed changes, or AI enhancement'}
timings={'pure':[x['seconds'] for x in baseline['completed']]}
for name in ['singularity_v2','hybrid_b20']:timings[name]=[x['seconds'] for x in remote['completed'] if x['model']==name]
report['generationSeconds']={name:{'chapters':values,'total':sum(values),'relativeToPure':sum(values)/sum(timings['pure'])} for name,values in timings.items()}
(P/'comparison-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(P/'timings.csv').write_text('model,chapter_1_seconds,chapter_2_seconds,total_seconds,relative_to_pure\n'+''.join(f"{name},{values[0]:.2f},{values[1]:.2f},{sum(values):.2f},{sum(values)/sum(timings['pure']):.4f}\n" for name,values in timings.items()))
print('COMPARISON COMPLETE',flush=True)
