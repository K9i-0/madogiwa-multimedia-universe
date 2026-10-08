from pathlib import Path
import subprocess,json
p=Path(__file__).resolve().parent;f=p.parent/'final_remotion_aeron_chua.mp4';m=json.loads((p/'src/edit-manifest.json').read_text())
subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True)
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]));v=next(s for s in r['streams'] if s['codec_type']=='video');assert int(v['nb_read_frames'])==m['composition']['durationInFrames'];assert(v['width'],v['height'],v['r_frame_rate'])==(1280,720,'30/1')
r['captionTextMatches']=all(d['caption'].replace('\n','')==d.get('captionText',d['text']) for d in m['dialogue']);r['subjectiveAudioReview']='not performed';r['fullDecode']='passed'
(p.parent/'qa_video.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(f),'-vf','fps=1/23,scale=426:240,tile=3x4','-frames:v','1',str(p/'out/contact.jpg')],check=True)
print('PASS',v['nb_read_frames'],'frames,',r['format']['duration'],'seconds')
