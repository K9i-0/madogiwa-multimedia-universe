"""One natural Irodori take per line. No ASR-driven retries or pronunciation rewriting."""
from pathlib import Path
import subprocess,os,json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];W=ROOT/'.local/doku-chikuwa-v5';W.mkdir(exist_ok=True)
lines=[('report','fukuchan','被害者は赤坂在住、40歳の男性。夕食のおでんを食べた直後に倒れたとみられます。'),('message','fukuchan','最期に残した言葉は……ちくわ。'),('deduction','yotan','被害者は、大のちくわ好きだった可能性が高い。'),('abbreviation','fukuchan','大のちくわ好き……略すと、だいちくわですね。'),('question','yotan','え、何で略した？'),('warning','fukuchan','おい！それは証拠品だ！'),('reaction','yotan','えぇ……')]
env={**os.environ,'IRODORI_TTS_CHECKPOINT':'Aratako/Irodori-TTS-v4-Large','IRODORI_UNCUT':'1'}
for k in ['IRODORI_CFG_SCALE_TEXT','IRODORI_DURATION_SCALE']:env.pop(k,None)
records=[]
for name,speaker,text in lines:
 ref=ROOT/'02_CHARACTERS/Fukuchan_voice.wav' if speaker=='fukuchan' else P/'yotan_reference_v3.wav'
 out=W/(name+'.wav')
 subprocess.run([str(ROOT/'tools/irodori_speak.sh'),text,str(out),str(ref),'100'],env=env,cwd=ROOT,check=True)
 records.append(dict(id=name,speaker=speaker,text=text,reference=str(ref.relative_to(ROOT)),output=out.name,seed=100,caption='',model='Aratako/Irodori-TTS-v4-Large',text_cfg='default (3)',duration_scale=1,uncut=True))
(W/'generation.json').write_text(json.dumps(dict(lines=records,asr_used=False,retry_count=0,pronunciation_review='user'),ensure_ascii=False,indent=2)+'\n')
