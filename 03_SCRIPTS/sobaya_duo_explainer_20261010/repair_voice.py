from pathlib import Path
import json,subprocess,os,shutil
root=Path(__file__).resolve().parents[2];ep=Path(__file__).resolve().parent;bak=root/'.local/sobaya-duo/voice-first';bak.mkdir(exist_ok=True)
rows=json.loads((ep/'dialogue.json').read_text())
fix={1:('そばやさんのことなら、わいも、よくしってるで。','0.85'),3:('しろいかめんに、そのきんにく。しょたいめんやと、ちょっとみがまえるな。','0.85'),8:('そのご、せきは、まどぎわから、ビルのそとのベランダへ、うつされます。','1'),14:('ところが、おみせは、ベランダごと、らっかしてしまいます。','1'),16:('さいわい、けがにんはいません。そばやさんは、かたづけをすすめ、おみせをさいけんします。','1'),17:('わいも、さいけんを、てつだったんやで。ちゃんとはたらいとるやろ。','0.85'),18:('ただ、おみせでは、やめさんかくほで、ビールえいきゅうむりょう、というキャンペーンも。','1'),19:('わいを、のみほうだいの、ひきかえけんに、せんといてくれ。','0.85'),21:('そばやさんとおると、でいりぐちまで、ふえるんやな。','0.85'),22:('そばやさんは、かいりきと、まえむきさで、まどぎわを、じぶんのいばしょにかえるひとです。','1')}
for i,(reading,scale) in fix.items():
 r=rows[i];src=ep/r['audio'];backup=bak/r['audio']
 if not backup.exists():shutil.copy2(src,backup)
 r['reading']=reading;r['durationScale']=scale
 env=dict(os.environ,IRODORI_UNCUT='1',IRODORI_CFG_SCALE_TEXT='5',IRODORI_DURATION_SCALE=scale)
 subprocess.run([str(root/'tools/irodori_speak.sh'),reading,str(src),str(root/r['reference']),str(r['seed'])],env=env,cwd=root,check=True)
(ep/'dialogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
