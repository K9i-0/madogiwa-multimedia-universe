from pathlib import Path
import json,subprocess,math,shutil,zipfile,hashlib
P=Path(__file__).resolve().parent;R=P.parents[1];S=R/'.claude/skills/minimax-h3-video/scripts'
plan=json.loads((P/'chapter_plan.json').read_text())
for ch in plan:
 name=ch['id'];shutil.copy2(P/'generated'/f'{name}_voice.wav',P/f'{name}_voice.wav')
 frames=17*math.ceil(((ch['voice_seconds']+0.6)*24-5)/17)+5
 if frames>362:raise ValueError('Split long chapter')
 ch['frames']=frames;ch['seconds']=frames/24
 prompt=f'''Animate this exact vertical 3:4 Japanese advertisement poster from <Picture 1>. Preserve the exact layout and the same man's exact face, curly light brown hair, round black spectacles, blue patterned shirt, skin texture and facial proportions. This is a living photograph, not a redesigned scene. Lock the camera and every pixel of the poster's yellow background, large white vertical lettering, small lower-left writing, lower-left name and purple product box. The man remains in precisely the same size and location as the reference, directly facing the camera. His shoulders, neck, hair and head stay completely still. Only his lips and jaw move subtly to speak; at most one natural blink. No nodding, no gestures, no zoom, no pan, no scene cuts. He speaks earnestly and matter-of-factly, without smiling. Use the male voice in <Audio 1> as the exact voice, timing and delivery reference. Read this Japanese passage ONCE, in order, with no repeated phrases and no added words: 「{ch['text']}」. This is one excerpt of a continuous speech. Begin at 0.2 seconds, finish in approximately {ch['voice_seconds']:.1f} seconds, then close the mouth. Do not restart the sentence to fill the remaining time. One male speaker only. Dry clear speech, no background music, no sound effects, no other voices. The text and objects in the image must remain static and unchanged throughout.'''
 (P/f'prompt_{name}.txt').write_text(prompt+'\n')
 subprocess.run(['python3',str(S/'build_workflow.py'),'--mode','r2v','--profile','480p-turbo','--width','480','--height','640','--frames',str(frames),'--prompt-file',str(P/f'prompt_{name}.txt'),'--image','poster.png','--audio',f'{name}_voice.wav','--out',str(P/f'{name}.json')],check=True)
(P/'chapter_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
job=P/'generated/h3-job';subprocess.run(['python3',str(S/'colab_h3.py'),'prepare',str(P/'ch01.json'),'--job',str(job)],check=True)
# Use the existing lifecycle with an episode-local sequential batch runner.
with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in ['setup_cuda.py','run_workflow.py']:z.write(S/f,f)
 z.write(P/'remote_batch.py','colab_remote.py')
 for f in ['poster.png','chapter_plan.json']+[f'{c["id"]}.json' for c in plan]+[f'{c["id"]}_voice.wav' for c in plan]:z.write(P/f,f)
f=job/'job.json';d=json.loads(f.read_text());d['bundle_sha256']=hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest();f.write_text(json.dumps(d,indent=2)+'\n')
