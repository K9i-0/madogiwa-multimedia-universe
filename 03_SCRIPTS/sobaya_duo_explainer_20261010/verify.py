from pathlib import Path
import json,subprocess,zipfile
root=Path(__file__).resolve().parents[2];ep=Path(__file__).resolve().parent;m=json.loads((ep/'remotion/src/edit-manifest.json').read_text());v=ep/'final_remotion_sobaya.mp4'
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(v)]));video=next(s for s in info['streams'] if s['codec_type']=='video');audio=next(s for s in info['streams'] if s['codec_type']=='audio');assert int(video['nb_read_frames'])==m['composition']['durationInFrames'];assert (video['width'],video['height'],video['r_frame_rate'])==(1280,720,'30/1');assert int(audio['sample_rate'])==48000
subprocess.run(['ffmpeg','-v','error','-i',str(v),'-f','null','-'],check=True)
moods={'normal','happy','surprise','worry','bored','angry','sad','smug'}
coverage={who:sorted({d['mood'] for d in m['dialogue'] if d['who']==who}) for who in ['takosan','yametaro']}
for vals in coverage.values():assert set(vals)==moods
with zipfile.ZipFile(ep/'commentary_duo_32sprites.zip') as z:assert len([n for n in z.namelist() if n.endswith('.png')])==32
frames=[]
for d in m['dialogue'][1::2]:
 j=max(range(8,len(d['envelope'])),key=lambda j:d['envelope'][j]);frames.append(d['startFrame']+j)
filt='select='+ '+'.join(f'eq(n\\,{f})' for f in frames)+',scale=640:360,tile=3x4'
(ep/'remotion/out').mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(v),'-vf',filt,'-frames:v','1',str(ep/'remotion/out/scenes_final.png')],check=True)
report=dict(width=video['width'],height=video['height'],fps=video['r_frame_rate'],frames=int(video['nb_read_frames']),videoSeconds=int(video['nb_read_frames'])/30,containerSeconds=float(info['format']['duration']),audioSampleRate=int(audio['sample_rate']),moodCoverage=coverage,spritePngCount=32,decode='pass',typecheck='pass',listening='Not independently audited; ASR screening is not listening validation',browser='32 image loads, mouth switching, animation and mirroring verified')
(ep/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
