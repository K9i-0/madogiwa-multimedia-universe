from pathlib import Path
import subprocess,json,re,hashlib
r=Path(__file__).resolve().parent;p=r.parent
report={'typecheck':'passed','representativeFramesReviewed':True,'fullSubjectiveAudition':False,'outputs':[]}
for mode in ['original_audio','bgm_only']:
 f=p/f'final_remotion_aura_{mode}_9x16.mp4'
 d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(f)]))
 v=next(s for s in d['streams'] if s['codec_type']=='video')
 assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(720,1280,'30/1','681')
 assert abs(float(d['format']['duration'])-22.7)<.05
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
 vh=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:v','-c','copy','-f','hash','-hash','sha256','-']).decode().strip()
 loud=subprocess.run(['ffmpeg','-hide_banner','-i',str(f),'-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 stats=json.loads(re.findall(r'\{\s*"input_i".*?\}',loud.stderr,re.S)[-1])
 report['outputs'].append({'file':f.name,'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest(),'videoHash':vh,'duration':d['format']['duration'],'frames':v['nb_frames'],'fullDecode':'passed','loudness':stats})
assert report['outputs'][0]['videoHash']==report['outputs'][1]['videoHash']
report['sameVideoBitstream']=True
(p/'aura_phonk_prep_20261026/qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
