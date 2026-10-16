import pathlib,json,re
base=pathlib.Path(__file__).resolve().parents[1]/'episodes'
manual={
'sobaya-desert-mega-beer':{2:['おい！持ってるビールを\n全部よこしな！！'],3:['そば屋神拳奥義！\nメガ生100烈拳！！'],6:['お前はもう酔っている']},
'sobaya-ai-pull-request':{1:['この実装任せた'],3:['プルリクエスト出しておいて'],6:['業務中は少ししか\nビール飲んじゃだめよ〜'],7:['少しでもダメや'],8:['反省してま〜す'],9:['平常運転や〜'],10:['平常運転や〜']},
'beer-only-engine-press-conference':{1:['ビールだけで動く\n夢のエンジンを発明したギュン'],3:['このそば屋エンジンの\n原理を紹介します。'],4:['スイッチオン'],8:['ご覧ください！\nビールが口に入ったことで','そば屋がスクワットを始め、\nその力でピストンが上下します'],9:['しかし、これでは\nピストンの動きが\nクランクシャフトを回す','一般的なエンジンの\n動きにならないのでは\nありませんか？'],10:['素晴らしい質問ギュン！！\nそうです！','ピストンを上下させているのは\nあくまでもビールの冷却と','チューブへビールを\n送るための作業です'],11:['実際に動力を生み出しているのは\nこの部分ギュン！'],15:['この夢のエンジンが広まれば\nビールだけで','あらゆる物を動かせるように\nなるギュン！']},
'fukuchan-yametaro-estimates':{1:['この機能、\nどんくらいで終わる？'],2:['1日ですね'],3:['ほんまか'],4:['あ、ログイン絡むんで\n3日で'],5:['増えた'],6:['決済も絡むんで2週間で'],7:['増えた'],8:['あー、既存のあれ触るんで\n1ヶ月ですね'],9:['もうええわ。\nで、正直いつ終わんねん'],10:['終わりはないですよ。\n運用がありますから'],11:['哲学始めんな'],12:['ちなみに“1日”は\n嘘やなかったです。\n手を動かす時間は1日なんで'],13:['残りの29日なんやねん'],14:['会議です'],15:['一番正直な見積もりやん']},
'madogiwa-manner-class-question-1':{1:['それでは第一問！'],2:['窓際に仕事を依頼する時には、\n必ず、窓際なのにすいません、','と断りを入れてからしか\n仕事を依頼してはならない。'],3:['いや、仕事を普通に頼むだけなら\n全然お願いしますとかで\nいいでしょ！','給料もらってるんだし。'],4:['相手を、窓際なのに、\nって呼ぶことが\n失礼に感じるよね。'],5:['いや、でも相手は窓際だよ？\n実は窓際って呼んだ方が\nいいかも。'],6:['はい、それではそろそろ\n回答をお願いします。'],8:['はい、それでは先生。\n正解をお願いします！'],9:['ぎゅん！正解はマル。'],10:['えぇーーー。'],11:['窓際ーー！！'],12:['変えなきゃよかった。'],13:['先生、解説をお願いします。'],14:['窓際が働くなんて奇跡だと\n理解してください！','窓際は働かないから\n窓際なんです。'],15:['それでもやむをえず\n何かを依頼する時には、','窓際なのにすいません、\nと断りを入れるのが\nマナーぎゅん。'],16:['そもそも窓際に仕事を\n依頼する時点でマナー違反やで！','絶対にダメなことや！'],17:['先生、そしたら\n働かないメンバーに','給料を払うのは\nもったいないと思うので、\nクビにしたらどうですか？'],18:['確かに。'],19:['良い質問です。クビにしたら\nその時には満足できるでしょう。','でも、第二第三の窓際が\n出てきてしまいます。'],20:['あと、クビになったら\nわいらが生きていけんやろ！','ちょっとは考えてくれやで。']}}
for slug,groups in manual.items():
 d=base/slug;align=json.loads((d/('alignment-refined.json' if (d/'alignment-refined.json').exists() else 'alignment.json')).read_text());selected={}
 for c in align:
  n=re.search(r'(?:ch|clip)(\d+)',c['file']);
  if not n or not c['text']:continue
  n=int(n[1]);score=max(c.get('localWaveScore',c['correlation']),c.get('localSpectralScore',c['spectralCorrelation']))
  if n not in selected or score>selected[n][0]:selected[n]=(score,c)
 out=[]
 for n,(_,c) in selected.items():
  parts=groups[n];lens=[len(t.replace('\n','')) for t in parts];total=sum(lens);a,b=c['speechStartSeconds'],c['speechEndSeconds'];at=a
  for i,t in enumerate(parts):
   end=b if i==len(parts)-1 else at+(b-a)*lens[i]/total
   out.append({'startFrame':round(at*24),'endFrame':round(end*24),'speaker':c['speaker'],'text':t,'referenceAudio':c['file']});at=end
 out.sort(key=lambda c:c['startFrame'])
 for i,c in enumerate(out):
  if i+1<len(out):c['endFrame']=min(c['endFrame'],out[i+1]['startFrame'])
  for line in c['text'].splitlines():
   if len(line)>15:print('LONG',slug,len(line),line)
 (d/'captions-reviewed.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
# Source is a combined three-run film; references carry run prefixes.
d=base/'sobayahazard-underground-continuation';a=json.loads((d/'alignment.json').read_text());text={'53_ch1_line1_fukuchan.wav':'こんにちゅあー','54_ch4_line1_fukuchan.wav':'そば屋がゾンビになってる…','54_ch4_line2_fukuchan.wav':'これはギュンギュンしてる\n場合じゃな〜〜〜い'};out=[]
for c in a:out.append({'startFrame':round(c['speechStartSeconds']*24),'endFrame':round(c['speechEndSeconds']*24),'speaker':'福ギュン','text':text[c['file']],'referenceAudio':c['file']})
out.sort(key=lambda c:c['startFrame']);(d/'captions-reviewed.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
