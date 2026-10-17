"""Technical delivery audit; not a substitute for human listening."""
from pathlib import Path
import subprocess,json,hashlib,wave
P=Path(__file__).resolve().parent;video=P.parent/'review_remotion_horror_aoyama_v7.mp4'
m=json.loads((P/'src/edit-manifest.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
vs=next(s for s in probe['streams'] if s['codec_type']=='video');aus=[s for s in probe['streams'] if s['codec_type']=='audio']
assert (vs['width'],vs['height'])==(1280,720)
assert int(vs['nb_read_frames'])==m['composition']['durationInFrames']
assert vs['r_frame_rate']=='30/1'
assert len(aus)==1 and aus[0]['sample_rate']=='48000'
r=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
assert r.returncode==0 and not r.stderr.strip(),r.stderr
level=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(video),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
loud=json.JSONDecoder().raw_decode(level.stderr[level.stderr.rfind('{'):])[0]
growl=m['characterAudio'][0]
nextvoice=next(r for r in m['narration'] if r['id']=='n0318')
assert growl['from']>=m['revealFrame'] and growl['from']+growl['duration']<nextvoice['from']
for event in m['characterAudio']:
 assert not any(event['from']<r['from']+r['duration'] and event['from']+event['duration']>r['from'] for r in m['narration'])
assert sum(r['text'].count('中口') for r in m['narration'])==2
assert all(m['captions'][i]['to']<=m['captions'][i+1]['from'] for i in range(len(m['captions'])-1))
for row in m['narration']:
 with wave.open(str(P/'public'/row['file'])) as wav:
  assert wav.getnframes()/wav.getframerate()<=row['duration']/30
for a,b in zip(m['narration'],m['narration'][1:]):
 assert a['from']+a['duration']<=b['from']
report={'frameCount':m['composition']['durationInFrames'],'seconds':m['composition']['durationInFrames']/30,'voiceClips':len(m['narration']),'captions':len(m['captions']),'shots':len(m['shots']),'nameOccurrences':sum(r['text'].count('中口') for r in m['narration']),'revealFrame':m['revealFrame'],'characterAudio':m['characterAudio'],'narrator':'VOICEVOX:青山龍星','speedScale':1.0,'pitchScale':0.0,'narrationOverlap':False,'manualListening':'not performed; automated screening only','music':'same separated reference; encounter variant and deliberately music-free evidence scenes; original track unconfirmed'}
report.update({'video':video.name,'bytes':video.stat().st_size,'sha256':hashlib.file_digest(video.open('rb'),'sha256').hexdigest(),'resolution':[vs['width'],vs['height']],'fps':vs['r_frame_rate'],'decodedFrames':int(vs['nb_read_frames']),'audioStreams':len(aus),'audioSampleRate':48000,'fullDecode':'passed; no reported errors','visualReview':'Separate visual inspection is recorded in review-v7.md; automated decode alone does not validate the images','integratedLUFS':float(loud['input_i']),'truePeakDbTP':float(loud['input_tp']),'loudnessRangeLU':float(loud['input_lra'])})
report['glimpseFrame']=m['glimpseFrame']
report['environmentalAudio']=m.get('environmentalAudio',[])
report['rhythm']=json.loads((P.parent/'preflight-v7.json').read_text())
report['workInserts']=m.get('inserts',[])
report['soundRegions']=m.get('soundRegions',[])
(P.parent/'video-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(P/'out/ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2))
byid={r['id']:r for r in m['narration']}
def range_clip(name,first,last,pad=1):
 a=byid[first]['from']/30-pad;b=(byid[last]['from']+byid[last]['duration'])/30+pad
 return name,max(0,a),b-max(0,a)
previews=[('reveal_v7',m['revealFrame']/30-14,42),
 range_clip('wife_v7','n0141','n0143'),
 range_clip('recollection_v7','n0207','n0219'),
 range_clip('moonlit_v7','n0073','n0078'),
 range_clip('absence_v7','n0167','n0168'),
 range_clip('monkeys_v7','n0048a','n0048d')]
for name,ss,duration in previews:
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(ss),'-i',str(video),'-t',str(duration),'-c:v','libx264','-preset','fast','-crf','21','-c:a','aac','-b:a','160k','-movflags','+faststart',str(P/'out'/f'preview_{name}.mp4')],check=True)
# Short review reel follows the user's four notes in story order, without
# adding title cards or new material to the actual film.
concat=P/'out/feedback-v7-concat.txt'
concat.write_text(''.join(f"file 'preview_{name}_v7.mp4'\n" for name in ['monkeys','moonlit','wife','absence']))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(P.parent/'review_feedback_v7.mp4')],check=True)
print(json.dumps(report,ensure_ascii=False),flush=True)
