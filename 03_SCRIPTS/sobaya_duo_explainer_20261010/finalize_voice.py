from pathlib import Path
import json,subprocess,os,shutil
root=Path(__file__).resolve().parents[2];ep=Path(__file__).resolve().parent;rows=json.loads((ep/'dialogue.json').read_text());backup=root/'.local/sobaya-duo/voice-second';backup.mkdir(exist_ok=True)
fix={18:('ただ、お店では、やめさんを捕まえると、ビールがずっと無料になるそうです。','ただ、おみせでは、やめさんをつかまえると、ビールがずっとむりょうになるそうです。'),19:('ワイを景品にするのは、やめてほしいわ。','わいをけいひんにするのは、やめてほしいわ。'),21:('そば屋さんとおると、壁まで通り道になるんやな。','そばやさんとおると、かべまでとおりみちになるんやな。'),22:('力が強くて、とても前向き。そば屋さんは、窓際を自分の居場所に変える人です。','ちからがつよくて、とてもまえむき。そばやさんは、まどぎわをじぶんのいばしょにかえるひとです。')}
rows[1]['text']='そば屋さんのことなら、ワイもよく知ってるで。'
for i,(text,reading) in fix.items():
 r=rows[i];shutil.copy2(ep/r['audio'],backup/r['audio']);r['text']=text;r['reading']=reading
 env=dict(os.environ,IRODORI_UNCUT='1',IRODORI_CFG_SCALE_TEXT='5',IRODORI_DURATION_SCALE=r['durationScale'])
 subprocess.run([str(root/'tools/irodori_speak.sh'),reading,str(ep/r['audio']),str(root/r['reference']),str(r['seed'])],env=env,cwd=root,check=True)
(ep/'dialogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
