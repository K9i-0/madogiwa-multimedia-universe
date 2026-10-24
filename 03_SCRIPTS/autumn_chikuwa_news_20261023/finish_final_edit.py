"""Level and verify the completed edit, without changing video pixels or generating media."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

P = Path(__file__).resolve().parent
src = P/'remotion/out/news_render.mp4'
dest = P/'final_remotion_news.mp4'
spec = json.loads((P/'remotion/src/edit-manifest.json').read_text())['final']

def run(args):
    return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)

analysis = run(['ffmpeg','-hide_banner','-i',src,'-af',
               'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
levels = json.loads(re.findall(r'\{[^{}]+\}',analysis)[-1])
filters = ('loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:'
           f'measured_I={levels["input_i"]}:measured_TP={levels["input_tp"]}:'
           f'measured_LRA={levels["input_lra"]}:measured_thresh={levels["input_thresh"]}:'
           f'offset={levels["target_offset"]}:print_format=json')
run(['ffmpeg','-y','-v','error','-i',src,'-map','0:v:0','-map','0:a:0','-c:v','copy',
     '-af',filters,'-ar','48000','-c:a','aac','-b:a','192k','-movflags','+faststart',dest])
probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams',
                      '-show_format','-of','json',dest]).stdout)
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1')
assert int(v['nb_read_frames'])==spec['composition']['durationInFrames']
assert a['sample_rate']=='48000'
run(['ffmpeg','-v','error','-i',dest,'-f','null','-'])
black=run(['ffmpeg','-hide_banner','-i',dest,'-vf','blackdetect=d=0.033:pix_th=0.05',
           '-an','-f','null','-']).stderr
black_segments=[s for s in black.splitlines() if 'black_start:' in s]
assert not black_segments,black_segments
levels_final=run(['ffmpeg','-hide_banner','-i',dest,'-vn','-af','ebur128=peak=true',
                 '-f','null','-']).stderr
summary=levels_final[levels_final.rfind('Summary:'):].split('[out#')[0].strip()
audit={'output':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
       'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],
       'videoFrames':int(v['nb_read_frames']),'videoDuration':float(v['duration']),
       'audioSampleRate':int(a['sample_rate']),'fullDecode':'pass','blackSegments':black_segments,
       'loudness':summary,'newVideoGenerationRequests':0,'newImageGenerationRequests':0,
       'speechGenerationAttempts':spec.get('coherentExpert',spec.get('beerExplanation',spec.get('feedback',{}))).get('generatedTakes',0),
       'visualAudit':'Cut boundaries, text, props and dense action contact sheets inspected.',
       'audioAudit':'Full-program and per-take ASR screened. Rare-word transcriptions differ across models. Loudness, source boundaries and decode checked. No auditory listening or real-time lip-sync approval claimed.',
       'limitations':['Original generated action retained; editing cannot reconstruct the physical bite or character acting.',
                      'Studio return uses a 12-frame still from the existing anchor recording.']}
(P/'final_edit_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(audit,ensure_ascii=False,indent=2))
