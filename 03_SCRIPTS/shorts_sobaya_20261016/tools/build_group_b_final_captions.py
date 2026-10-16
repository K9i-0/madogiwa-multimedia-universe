import pathlib,json
base=pathlib.Path('03_SCRIPTS/shorts_sobaya_20261016/episodes')
def save(slug,captions,notes):
 d=base/slug
 for c in captions:
  assert len(c['text'].splitlines())<=3,c
  assert max(map(len,c['text'].splitlines()))<=15,c
 (d/'captions-reviewed.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2)+'\n')
 m=json.loads((d/'shorts-manifest.json').read_text());m['captions']=captions;m['captionEvidence']=notes;(d/'shorts-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

def cue(a,b,s,t,**kw):return dict(startFrame=round(a*24),endFrame=round(b*24),speaker=s,text=t,**kw)
save('sobaya-beer-battery',[
 cue(.5,4.84,'福ギュン','そば屋、最近人が変わったように\nよく働くなー'),
 cue(8.18,10.6,'福ギュン','え、そば屋？\nどうしたギュン？'),
 cue(15.44,16.55,'よーたん','あ、切れちゃったか'),
 cue(16.74,17.25,'福ギュン','え？'),
 cue(26.1,27.05,'福ギュン','おお！'),
 cue(27.56,30.08,'福ギュン','エンジニアってすごいわね！'),
],{'text':'Actual source Whisper transcript corroborates local original script_approach2_rich_30s.md. Canonical display name 福ギュン; supplied later Studio prompt cast differs and was not used to invent source dialogue.','timing':'Whisper segment windows refined with source silencedetect -30dB d0.12; first speech .509s, second 8.18s, Yotan 15.44s, short response 16.74s, exclamation 26.1s, final line 27.56s.','asr':'../../group-b-critical-asr.json'})
save('sobaya-yametaro-dismissal-notice',[],{'text':'Studio generation prompt describes action soundscape without dialogue. Supplied reference WAVs have no reliable match in adopted final (waveform <.15). Source ASR returned incoherent fragments, so no fabricated dialogue captions added. Original source audio retained.','asr':'../../group-b-critical-asr.json'})
d=base/'yametaro-ultra-dry-home-shopping';a={c['file']:c for c in json.loads((d/'alignment.json').read_text())}
out=[]
def aligned(file,texts):
 c=a[file];start=c['speechStartSeconds'];end=c['speechEndSeconds'];lens=[len(t.replace('\n','')) for t in texts];total=sum(lens)
 for i,t in enumerate(texts):
  last=end if i==len(texts)-1 else start+(c['speechEndSeconds']-c['speechStartSeconds'])*lens[i]/total
  out.append(cue(start,last,c['speaker'],t,referenceAudio=file));start=last
aligned('clip1_line1_yametaro.wav',['今日もたくさんバグを作って\n疲れたわ〜テレビでも見よ'])
aligned('clip3_line1_fukuchan.wav',['福ちゃんショッピングの\nコーナーぎゅん〜'])
aligned('clip4_line1_fukuchan.wav',['今日ご紹介するのはこれ！','そば屋肥料\nめっちゃでかくなーるTwo'])
aligned('clip5_line1_fukuchan.wav',['ではこちらの映像を\nご覧くださいぎゅん'])
aligned('clip10_line1_narrator.wav',['持っているものは何ですか？'])
# Chapters 11/12 use regenerated voices; low waveform match. Source ASR confirms text.
out += [cue(43.4,45.0,'そば屋','これはですね。'),cue(45.0,48.0,'そば屋','そば屋肥料\nめっちゃでかくなーる\nTwoです。'),cue(48.5,50.7,'そば屋','そば屋肥料\nめっちゃでかくなーるTwoを\n使うと'),cue(50.7,53.15,'そば屋','どんな野菜でも\nビールになるんです')]
aligned('clip17_line1_sobaya.wav',['採れたてのビールだ！\nいただきまーす！'])
aligned('clip18_line1_sobaya.wav',['キンキンに冷えてやがる！！\n美味い！！'])
aligned('clip19_line1_fukuchan.wav',['いかがでしたか？\nどんな野菜もビールになるって\n素敵じゃないですか？'])
out += [cue(85.237,88.057,'福ギュン','今ならなんと\n6缶パックで1500円ギュン',referenceAudio='clip20_line1_fukuchan.wav'),cue(88.057,89,'福ギュン','安すぎてギュン',referenceAudio='clip20_line1_fukuchan.wav')]
out.sort(key=lambda c:c['startFrame'])
save('yametaro-ultra-dry-home-shopping',out,{'text':'Studio dialogue prompt + actual source/attached reference audio ASR. Historical spoken 福ちゃん retained, speaker label 福ギュン. Narrator uncertain initial syllable omitted; audible phrase 持っているものは何ですか retained. Offer 6缶/1500円 corroborated by prompt offer text.','timing':'Matched original/accelerated reference audio via timestamp-preserving waveform and spectral correlation; chapters11/12 regenerated speech validated by ASR and chapter windows, approximate subphrase boundaries.','asr':'../../group-b-critical-asr.json'})
