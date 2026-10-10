from pathlib import Path
import os,json,subprocess,hashlib
root=Path(__file__).resolve().parents[2];ep=Path(__file__).resolve().parent
spec=[
('takosan','今日は、窓際族物語のそば屋さんを紹介します。','normal','intro'),
('yametaro','そば屋さんのことなら、ワイもよう知ってるで。','smug','intro'),
('takosan','四十一歳。身長百八十センチ、体重百キロ。かなりの体格です。','surprise','profile'),
('yametaro','白い仮面に、その筋肉。初対面やと、ちょっと身構えるな。','surprise','profile'),
('takosan','でも、見た目は怖くても優しい人。ビールがあると、ご機嫌です。','happy','kind'),
('yametaro','話しかけるきっかけが、乾杯で済むのは助かるわ。','happy','kind'),
('takosan','入社したときの椅子は、段ボール製のアーロンチュアでした。','bored','chair'),
('yametaro','名前だけ聞いたら、高級な椅子やと思うやろ。','bored','chair'),
('takosan','その後、席は窓際から、ビルの外のベランダへ移されます。','worry','balcony'),
('yametaro','窓際って、窓の内側ちゃうんか。冬は寒いやろ。','worry','balcony'),
('takosan','本人は、ビールが冷えたままなのでメリット、と受け止めます。','smug','positive'),
('yametaro','社員の席を、冷蔵庫みたいに扱ったらあかんやろ。','angry','positive'),
('takosan','そして、そのベランダに立ち飲み処を開きました。','normal','bar'),
('yametaro','席を戻してもらうより先に、店を開いたんか。','normal','bar'),
('takosan','ところが、お店はベランダごと落下してしまいます。','sad','fall'),
('yametaro','せっかくの店が。これは、さすがに落ち込むわ。','sad','fall'),
('takosan','幸い、けが人はいません。そば屋さんは片付けを進め、お店を再建します。','happy','rebuild'),
('yametaro','ワイも、再建を手伝ったんやで。ちゃんと働いとるやろ。','smug','rebuild'),
('takosan','ただ、お店では、やめさん確保でビール永久無料、というキャンペーンも。','angry','campaign'),
('yametaro','ワイを、飲み放題の引き換え券にせんといてくれ。','angry','campaign'),
('takosan','後には二人で捕まりますが、壁を破って脱走しています。','surprise','escape'),
('yametaro','そば屋さんとおると、出入り口まで増えるんやな。','worry','escape'),
('takosan','そば屋さんは、怪力と前向きさで、窓際を自分の居場所に変える人です。','smug','summary'),
('yametaro','次は普通の入り口から、お店に飲みに行きたいわ。','happy','summary')]
rows=[]
for i,(who,text,mood,scene) in enumerate(spec):
 ref='Takosan' if who=='takosan' else 'Yametaro';seed=43 if who=='takosan' else 7;scale='1' if who=='takosan' else '0.70';name=f'line{i+1:02}_{who}.wav'
 r=dict(who=who,text=text,mood=mood,scene=scene,audio=name,seed=seed,durationScale=scale,model='Aratako/Irodori-TTS-v4.1-Small',caption='',textCfg=5,uncut=True,reference=f'02_CHARACTERS/{ref}_voice.wav')
 rows.append(r)
(ep/'dialogue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
for r in rows:
 out=ep/r['audio'];key=hashlib.sha256(json.dumps(r,ensure_ascii=False,sort_keys=True).encode()+ (root/r['reference']).read_bytes()).hexdigest();meta=out.with_suffix('.key')
 if out.exists() and meta.exists() and meta.read_text()==key:continue
 env=dict(os.environ,IRODORI_UNCUT='1',IRODORI_CFG_SCALE_TEXT='5',IRODORI_DURATION_SCALE=r['durationScale'])
 subprocess.run([str(root/'tools/irodori_speak.sh'),r['text'],str(out),str(root/r['reference']),str(r['seed'])],cwd=root,env=env,check=True);meta.write_text(key)
