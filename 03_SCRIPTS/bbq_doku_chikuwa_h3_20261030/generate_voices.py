import json,os,hashlib,shutil,subprocess,time
from pathlib import Path
EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
LINES=[
('ch1_yotan','yotan','やっぱバーベキューと言ったら、ちくわだよなー'),
('ch1_sobaya','sobaya','この焼き目がいいんですよ！'),
('ch1_yametaro','yametaro','端っこのカリカリがうまいねんな'),
('ch2_sobaya','sobaya','乾杯！'),
('ch3_sobaya','sobaya','これ、いい感じに焼けました'),
('ch3_yotan','yotan','お、うまそう'),
('ch4_yametaro','yametaro','あ、これワイが買った毒ちくわや！'),
('ch4_yotan','yotan','なんで買ってるんだよ'),
('ch5_sobaya','sobaya','これ、毒ちくわです'),
]
rec=EP/'voice-records.json'; records=json.loads(rec.read_text()) if rec.exists() else {}
for id,who,text in LINES:
    out=EP/(id+'.wav')
    if id in records and out.exists():continue
    ref=ROOT/'02_CHARACTERS'/({'yotan':'Yotan','sobaya':'Sobaya','yametaro':'Yametaro'}[who]+'_voice.wav')
    seed={'sobaya':42,'yotan':100,'yametaro':7}[who]
    env=os.environ.copy();env['IRODORI_CFG_SCALE_TEXT']='5';env['IRODORI_UNCUT']='1';env['IRODORI_DURATION_SCALE']='0.70' if who=='yametaro' else '1.0'
    candidate=EP/'generated/voices'/out.name
    print('GENERATING',id,flush=True);start=time.time()
    with (candidate.with_suffix('.log')).open('w') as log:
        subprocess.run([str(ROOT/'tools/irodori_speak.sh'),text,str(candidate),str(ref),str(seed)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    if who=='sobaya':subprocess.run([str(ROOT/'tools/sobaya_monsterize.sh'),str(candidate),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    else:shutil.copy2(candidate,out)
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)],text=True))
    records[id]={'speaker':who,'text':text,'file':out.name,'model':'Aratako/Irodori-TTS-v4-Large' if who=='sobaya' else 'Aratako/Irodori-TTS-v4.1-Small','reference':str(ref.relative_to(ROOT)),'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'seed':seed,'caption':'','cfg_text':5,'duration_scale':float(env['IRODORI_DURATION_SCALE']),'uncut':True,'postprocess':'sobaya_monsterize.sh' if who=='sobaya' else None,'duration':duration,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'generation_seconds':time.time()-start,'audit':'not yet listened; input for H3, not a final dubbed audio'}
    rec.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print('DONE',id,duration,flush=True)
