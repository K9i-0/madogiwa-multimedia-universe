from pathlib import Path
import json,subprocess,sys
P=Path(__file__).resolve().parent;EP=P.parent;results=Path(sys.argv[1]).resolve()
def run(a):subprocess.run(a,check=True)
def ff(*args):run(['ffmpeg','-v','error','-y',*map(str,args)])
raw=EP/'h3_compare_raw_turbo8_480p.mp4';native=EP/'h3_compare_turbo8_480p_native.mp4';final=EP/'final_h3_compare_turbo8_480p.mp4';compare=EP/'final_h3_compare_turbo8_768p_vs_480p.mp4'
filt='[0:v]trim=end_frame=360,setpts=PTS-STARTPTS[v0];[1:v]trim=end_frame=360,setpts=PTS-STARTPTS[v1];[0:a]atrim=end=15,asetpts=PTS-STARTPTS[a0];[1:a]atrim=end=15,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
ff('-i',results/'turbo8_480p_ch01.mp4','-i',results/'turbo8_480p_ch02.mp4','-filter_complex',filt,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf',18,'-c:a','aac','-b:a','192k','-t',30,'-movflags','+faststart',raw)
master=EP/'remotion/public/shopping_irodori_instrumental_master_30s.wav'
ff('-i',raw,'-i',master,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',30,'-movflags','+faststart',native)
ff('-i',native,'-vf','scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1','-c:v','libx264','-preset','fast','-crf',18,'-c:a','copy','-movflags','+faststart',final)
font='/System/Library/Fonts/Helvetica.ttc';filters=[]
for i,label in enumerate(['Turbo8 1344x768','Turbo8 864x480']):filters.append(f"[{i}:v]scale=672:384:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=672:432:(ow-iw)/2:48+(384-ih)/2,setsar=1,drawtext=fontfile='{font}':text='{label}':fontsize=26:fontcolor=white:x=(w-tw)/2:y=10[v{i}]")
filters.append('[v0][v1]hstack=inputs=2[v]')
ff('-i',EP/'final_h3_compare_turbo8.mp4','-i',native,'-filter_complex',';'.join(filters),'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','fast','-crf',18,'-c:a','copy','-t',30,'-movflags','+faststart',compare)
outputs=[]
for f,w,h in [(raw,864,480),(native,864,480),(final,1280,720),(compare,1344,432)]:
 d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(f)]));v=next(x for x in d['streams'] if x['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(w,h,'24/1',720);assert any(x['codec_type']=='audio' for x in d['streams']);ff('-i',f,'-f','null','-');outputs.append({'file':f.name,'width':w,'height':h,'frames':720,'decode':'passed'})
remote=json.loads((results/'status.json').read_text());baseline=json.loads((EP/'h3_turbo8_20261027/comparison-result.json').read_text());times=[x['seconds'] for x in remote['completed']];base=baseline['generationSeconds']['turbo8']['total']
report={'baselineReused':True,'baselineSeconds':base,'newRun':remote,'generationSeconds':sum(times),'speedup':base/sum(times),'outputs':outputs,'qualityReview':'User judges; no quality rerolls','audioPolicy':'Same adopted Irodori master; raw retains generated audio'}
(P/'comparison-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(P/'timings.csv').write_text('variant,generation_seconds\n'+f'turbo8_768p,{base:.3f}\nturbo8_480p,{sum(times):.3f}\n')
print('COMPARISON COMPLETE',flush=True)
