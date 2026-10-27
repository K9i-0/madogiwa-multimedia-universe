"""Generate canonical Irodori voices; resume without overwriting adopted takes."""
import argparse, hashlib, json, os, subprocess, time
from pathlib import Path

EP = Path(__file__).resolve().parent
ROOT = EP.parents[1]
CAPTION = '落ち着いた地方局ニュース読み。標準語で、明瞭かつ均一な速度、抑制された抑揚で真面目に話す。'
CAST = {
    'anchor': ('YumeTeleAnchor_voice.wav',2026,CAPTION),
    'sobaya': ('Sobaya_voice.wav',42,'落ち着いた会話調で、淡々と話す。'),
    'fukuchan': ('Fukuchan_voice.wav',100,'明るく人懐っこく、自然な会話調で話す。'),
    'yametaro': ('Yametaro_voice.wav',7,''),
    'takosan': ('Takosan_voice.wav',43,''),
}

def main():
    p=argparse.ArgumentParser();p.add_argument('--group',choices=['dialogue','narration','all'],default='all');a=p.parse_args()
    d=json.loads((EP/'content.json').read_text())
    dialogue=[line for ch in d['chapters'] for line in ch['dialogue']]
    # Generate Large first, then release it before the Small actor voices.
    dialogue.sort(key=lambda x: x['speaker']!='sobaya')
    narration=d['opening']+[line for ch in d['chapters'] for line in [ch['question']]+([f['line'] for f in ch['feedback']] if 'feedback' in ch else [ch['explanation']])]+d['ending']
    lines=dialogue if a.group=='dialogue' else narration if a.group=='narration' else dialogue+narration
    tmp=EP/'generated'/'voices';tmp.mkdir(parents=True,exist_ok=True)
    records_path=EP/'voice-records.json'
    records=json.loads(records_path.read_text()) if records_path.exists() else {}
    for line in lines:
        name,seed,caption=CAST[line['speaker']];ref=ROOT/'02_CHARACTERS'/name
        out=EP/(line['id']+'_'+line['speaker']+'.wav')
        if out.exists() and line['id'] in records:
            if any(records[line['id']].get(k)!=line.get(k) for k in ('speaker','text','reading')):
                raise ValueError('Existing take differs; use a new revision ID: '+line['id'])
            print('EXISTS',line['id'],flush=True);continue
        env=os.environ.copy();env['IRODORI_CFG_SCALE_TEXT']='5'
        if line['speaker']=='yametaro':env.update(IRODORI_UNCUT='1',IRODORI_DURATION_SCALE='0.70')
        candidate=tmp/(line['id']+'.wav')
        args=[str(ROOT/'tools/irodori_speak.sh'),line.get('reading',line['text']),str(candidate),str(ref),str(seed)]
        if caption:args.append(caption)
        start=time.time();print('GENERATING',line['id'],line['text'],flush=True)
        with (tmp/(line['id']+'.log')).open('w') as f:
            subprocess.run(args,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
        if line['speaker']=='sobaya':
            subprocess.run([str(ROOT/'tools/sobaya_monsterize.sh'),str(candidate),str(out)],check=True)
        else:out.write_bytes(candidate.read_bytes())
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)],text=True))
        records[line['id']]={**line,'file':out.name,'reference':str(ref.relative_to(ROOT)),'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'seed':seed,'caption':caption,'model':'Aratako/Irodori-TTS-v4-Large' if line['speaker']=='sobaya' else 'Aratako/Irodori-TTS-v4.1-Small','cfg_text':5,'duration_scale':0.70 if line['speaker']=='yametaro' else 1.0,'uncut':line['speaker']=='yametaro','duration':duration,'generation_seconds':time.time()-start,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'status':'generated; audit pending'}
        temporary=records_path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');temporary.replace(records_path)
        print('DONE',line['id'],duration,flush=True)

if __name__=='__main__':main()
