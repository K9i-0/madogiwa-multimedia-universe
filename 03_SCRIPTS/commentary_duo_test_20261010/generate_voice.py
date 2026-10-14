import subprocess,os,json
from pathlib import Path
root=Path.cwd(); out=root/'03_SCRIPTS/commentary_duo_test_20261010'
lines=[('takosan','今日は、立ち絵を使った解説のテストです。','normal'),('yametaro','ワイらも、ついに解説する側になったんやな。','normal'),('takosan','話すと口が動いて、表情も変わります。','happy'),('yametaro','おお、ちゃんと動いとる。仕事してるみたいや。','surprise'),('takosan','見た目が動いても、仕事が進むとは限りません。','normal'),('yametaro','初回から、ワイに厳しすぎるやろ。','surprise')]
data=[]
for i,(who,text,mood) in enumerate(lines):
 name=f'line{i+1:02}_{who}.wav'; ref='Takosan' if who=='takosan' else 'Yametaro'; seed=43 if who=='takosan' else 7
 env=dict(os.environ,IRODORI_UNCUT='1',IRODORI_CFG_SCALE_TEXT='5',IRODORI_DURATION_SCALE='1' if who=='takosan' else '0.70')
 subprocess.run([str(root/'tools/irodori_speak.sh'),text,str(out/name),str(root/f'02_CHARACTERS/{ref}_voice.wav'),str(seed)],env=env,check=True)
 data.append(dict(who=who,text=text,mood=mood,audio=name,seed=seed,durationScale=env['IRODORI_DURATION_SCALE']))
 (out/'dialogue.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
