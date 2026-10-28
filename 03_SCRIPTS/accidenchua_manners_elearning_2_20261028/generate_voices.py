"""Canonical actors and a new, original deadpan training-film narrator."""
import argparse, hashlib, json, os, shutil, subprocess, time
from pathlib import Path

EP = Path(__file__).resolve().parent
ROOT = EP.parents[1]
CAPTION = '昔の企業研修ビデオの男性ナレーター。中低音の落ち着いた声。標準語の明瞭な発音で、一文ずつ丁寧に、ややゆっくり、淡々と説明する。冗談を言う調子にはしない。'

def main():
    p=argparse.ArgumentParser();p.add_argument('--group',choices=['dialogue','narration','all'],default='all');args=p.parse_args()
    data=json.loads((EP/'content.json').read_text())
    lines=sorted(data['dialogue'],key=lambda x:x['speaker']!='sobaya') if args.group!='narration' else []
    if args.group!='dialogue':lines+=data['narration']
    generated=EP/'generated/voices';generated.mkdir(parents=True,exist_ok=True)
    rec=EP/'voice-records.json';records=json.loads(rec.read_text()) if rec.exists() else {}
    for line in lines:
        out=EP/(line['id']+'.wav');who=line['speaker']
        if line['id'] in records and out.exists():
            assert records[line['id']]['text']==line['text'];print('EXISTS',out.name,flush=True);continue
        seed={'sobaya':42,'fukuchan':100,'narrator':2801}[who]
        model='Aratako/Irodori-TTS-v4-Large' if who=='sobaya' else 'Aratako/Irodori-TTS-v4.1-Small'
        caption=CAPTION if who=='narrator' else '丁寧な会話調で、自然にはっきり話す。' if who=='fukuchan' else '落ち着いた会話調。大きさに少し戸惑いながら、淡々と尋ねる。'
        ref=ROOT/'02_CHARACTERS'/('Sobaya_voice.wav' if who=='sobaya' else 'Fukuchan_voice.wav')
        if who=='narrator':ref=EP/'narrator_reference.wav'
        candidate=generated/out.name
        env=os.environ.copy();env['IRODORI_CFG_SCALE_TEXT']='5'
        if who=='narrator' and not ref.exists():
            cmd=[str(ROOT/'.local/Irodori-TTS/.venv/bin/python'),'infer.py','--hf-checkpoint',model,'--no-ref','--text',line.get('reading',line['text']),'--caption',caption,'--seed',str(seed),'--cfg-scale-text','5','--output-wav',str(candidate)]
            cwd=ROOT/'.local/Irodori-TTS';ref_used=None
        else:
            cmd=[str(ROOT/'tools/irodori_speak.sh'),line.get('reading',line['text']),str(candidate),str(ref),str(seed),caption];cwd=ROOT;ref_used=ref
        print('GENERATING',line['id'],flush=True);start=time.time()
        with (generated/(line['id']+'.log')).open('w') as log:subprocess.run(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        if who=='sobaya':subprocess.run([str(ROOT/'tools/sobaya_monsterize.sh'),str(candidate),str(out)],check=True)
        else:shutil.copy2(candidate,out)
        if who=='narrator' and not ref.exists():shutil.copy2(out,ref)
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)],text=True))
        records[line['id']]={**line,'file':out.name,'model':model,'seed':seed,'caption':caption,'cfg_text':5,'duration_scale':1,'reference':str(ref_used.relative_to(ROOT)) if ref_used else None,'reference_sha256':hashlib.sha256(ref_used.read_bytes()).hexdigest() if ref_used else None,'duration':duration,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'generation_seconds':time.time()-start,'audit':'pending'}
        rec.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print('DONE',line['id'],duration,flush=True)

if __name__=='__main__':main()
