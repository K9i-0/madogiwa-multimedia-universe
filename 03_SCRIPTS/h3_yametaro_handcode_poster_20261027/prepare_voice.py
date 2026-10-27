from pathlib import Path
import os,subprocess,json
P=Path(__file__).resolve().parent;R=P.parents[1]
lines=[
'時代に負けてたまるか。正直に伝えます。来年からアクシデンチュアの実装工数が5割ほど増加します。',
'AIでただコードを生成するだけなんてしたくなくて。一行一行、人の手でコードを書くことで工数をアップしました。',
'そんな私たちの思いを、本日、この投稿に掲載しています。時代に負けてたまるか。']
plan=[]
for i,text in enumerate(lines,1):
 name=f'ch{i:02d}';out=P/'generated'/f'{name}_voice.wav'
 env=os.environ.copy();env.update(IRODORI_UNCUT='1',IRODORI_CFG_SCALE_TEXT='5')
 if not out.exists():
  with (P/'generated'/f'{name}_tts.log').open('w') as log:
   subprocess.run([str(R/'tools/irodori_speak.sh'),text,str(out),str(R/'02_CHARACTERS/Yametaro_voice.wav'),'7'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 seconds=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)]))
 plan.append({'id':name,'text':text,'voice_seconds':seconds})
 print(name,seconds,flush=True)
(P/'chapter_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
