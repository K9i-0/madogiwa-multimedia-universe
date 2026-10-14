from pathlib import Path
import json,subprocess,shutil,os,wave,hashlib
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];W=ROOT/'.local/doku-chikuwa-v4';R=P/'remotion';PUB=R/'public'
def pcm(path):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ac','2','-ar','48000','-f','s16le','-']),dtype='<i2').reshape(-1,2).copy()
def save(path,a):
 with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(a.astype('<i2').tobytes())
for n in ['report','message','abbreviation','warning','yotan_reaction']:
 dst=P/(n+'_v4.wav')
 if not dst.exists():shutil.copy2(W/(n+'.wav'),dst)
for n in ['wan3_entrance_inserts_v4_480p.mp4','endcard_oden_glitter.png']:
 if not (PUB/n).exists():os.link(P/n,PUB/n)
# Rebuild the reused scene's bed from retained v3 PCM, including unchanged Yotan and Sobaya.
a=pcm(P/'wan3_result_v2_480p.mp4')
for filename,start,end,gain in [('yotan_deduction_v3.wav',6.27,10.4,1.0),('yotan_question_v3.wav',15.2,17.45,1.0),('sobaya_doku_chikuwa_v2.wav',24.08,26.5,1.2613616324107835)]:
 x=pcm(P/filename);s0,e0=round(start*48000),round(end*48000);a[s0:e0]=0
 x=np.rint(x.astype(float)*gain).astype('<i2')
 if filename.startswith('sobaya'):x[:240]=np.rint(x[:240]*np.linspace(0,1,240)[:,None]).astype('<i2')
 a[s0:s0+len(x)]=x
for name,fr,to in [('abbreviation',320,450),('warning',595,679)]:
 x=pcm(P/(name+'_v4.wav'));s,e=fr*1600,to*1600;assert len(x)<=e-s
 a[s:e]=0;a[s:s+len(x)]=x
insert=pcm(P/'wan3_entrance_inserts_v4_480p.mp4')
shots=[]
def shot(kind,file,start,duration,source=0):shots.append(dict(kind=kind,file=file,from_=start,duration=duration,sourceStart=source))
# 11.4s incident report, followed by a separate entrance scene.
shot('video','wan3_result_v2_480p.mp4',0,107,0)
shot('image','oden_toxic_c_reference.png',107,121)
shot('image','blood_message_reference.png',228,114)
shot('video','wan3_entrance_inserts_v4_480p.mp4',342,218,0)
# Reused investigation. Cut to the evidence while Fukugyun smiles in the original.
shot('video','wan3_result_v2_480p.mp4',560,216,165)
shot('image','oden_toxic_c_reference.png',776,72)
shot('video','wan3_result_v2_480p.mp4',848,73,453)
# Late intrusion, then the existing eating / drinking / diagnosis / fall.
shot('video','wan3_entrance_inserts_v4_480p.mp4',921,142,218)
shot('video','wan3_result_v2_480p.mp4',1063,374,526)
subprocess.run(['ffmpeg','-y','-v','error','-ss','29.6','-i',str(P/'wan3_result_v2_480p.mp4'),'-frames:v','1',str(PUB/'ending_hold.png')],check=True)
shot('image','ending_hold.png',1437,18)
shot('image','endcard_oden_glitter.png',1455,36)
for s in shots:s['from']=s.pop('from_')
m=dict(fps=30,width=1280,height=720,durationInFrames=1491,shots=shots,audio='master_v4.wav',endcardFrames=36)
(R/'src/edit-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
master=np.zeros((1491*1600,2),dtype='<i2')
def put(x,frame):s=frame*1600;assert s+len(x)<=len(master);master[s:s+len(x)]=x
put(pcm(P/'report_v4.wav'),3);put(pcm(P/'message_v4.wav'),237)
put(insert[:218*1600],342);put(a[165*1600:526*1600],560);put(insert[218*1600:360*1600],921);put(a[526*1600:900*1600],1063)
reaction=pcm(P/'yotan_reaction_v4.wav');put(reaction,1410)
save(PUB/'master_v4.wav',master)
refs=[{'speaker':'福ギュン','reference':'02_CHARACTERS/Fukuchan_voice.wav','seed':100,'model':'Aratako/Irodori-TTS-v4-Large','lines':['report_v4.wav','message_v4.wav','abbreviation_v4.wav','warning_v4.wav']},{'speaker':'よーたん','reference':'yotan_reference_v3.wav','seed':100,'lines':['yotan_deduction_v3.wav','yotan_question_v3.wav','yotan_reaction_v4.wav']},{'speaker':'そば屋','reference':'02_CHARACTERS/Sobaya_voice.wav','line':'sobaya_doku_chikuwa_v2.wav','processing':'unchanged canonical Irodori Large + monsterize'}]
(P/'edit_v4_record.json').write_text(json.dumps(dict(composition='DokuChikuwa',durationInFrames=1491,fps=30,reused_source='wan3_result_v2_480p.mp4',insert_source='wan3_entrance_inserts_v4_480p.mp4',voices=refs,voice_generation=[['report','被害者は赤坂在住、四十歳の男性。夕食のおでんを食べた直後に倒れたとみられます。','落ち着いた刑事の報告。自然な速さで明瞭に話す。'],['message','最期に残した言葉は、ちくわ。','真剣な報告。'],['abbreviation','だいのちくわ好き。りゃくすと、だいちくわですね。','真剣に淡々と話す。'],['warning','おい！それは、しょうこひんだ！','鋭く制止する。'],['yotan_reaction','えぇ……。','信じられないものを見て、困惑して小さく声を漏らす。']],text_cfg=5,uncut=True,duration_scale=1,endcard='endcard_oden_glitter.png',generation_tool='built-in image_gen',listening_verified=False,precise_lip_sync_verified=False),ensure_ascii=False,indent=2)+'\n')
print('Prepared',1491/30,'seconds')
