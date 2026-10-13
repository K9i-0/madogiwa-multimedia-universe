"""Preserve only adopted voice inputs, without rewriting the approved screenplay."""
from pathlib import Path
import json,hashlib,os,re
P=Path(__file__).resolve().parent;m=json.loads((P/'src/edit-manifest.json').read_text());items=[]
previous={}
for f in P.parent.glob('*adopted_audio*.json'):
 try:
  for x in json.loads(f.read_text()).get('audio',[]):previous[x['sha256']]=x['file']
 except (KeyError,TypeError):pass
for d in m['dialogue']:
 src=P/'public'/d['audio'];digest=hashlib.sha256(src.read_bytes()).hexdigest()
 dst=P.parent/previous.get(digest,f'v7_{d["id"]}_{d["who"]}.wav')
 if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
 else:os.link(src,dst)
 items.append({'id':d['id'],'file':dst.name,'publicAudio':d['audio'],'sha256':digest,'who':d['who']})
(P.parent/'adopted_audio_v7.json').write_text(json.dumps({'version':7,'audio':items},ensure_ascii=False,indent=2)+'\n')
chapters=[]
for d in m['dialogue']:
 if not any(c['chapter']==d['chapter'] for c in chapters):
  secs=0 if not chapters else d['startFrame']//30
  chapters.append({'chapter':d['chapter'],'startFrame':0 if not chapters else d['startFrame'],'youtubeTime':f'{secs//60:02}:{secs%60:02}'})
(P.parent/'chapters_v7.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2)+'\n')
p=P.parent/'youtube_description.txt';s=p.read_text();a=s.index('チャプター\n');b=s.index('\n制作リポジトリ',a)
s=s[:a]+'チャプター\n'+'\n'.join(c['youtubeTime']+' '+re.sub(r'^\d+\. ','',c['chapter']) for c in chapters)+'\n'+s[b:]
s=s.replace('今後紹介予定のh3さんのリポジトリ','今後紹介予定のMiniMax H3の制作手法（同僚のリポジトリ）').replace('h3さんの費用差・所要時間','MiniMax H3を使う手法の費用差・所要時間')
s=s.replace('通常表示価格：480p $0.05/秒、720p $0.10/秒、1080p $0.20/秒。','通常表示価格：480p $0.05/秒、720p $0.10/秒、1080p $0.20/秒。\n説明用の固定換算1ドル160円で、30秒あたり約240円／480円／960円。480p・30秒を3回生成すると約720円です。実際の請求額は為替・割引・決済条件等で変わります。')
s=s.replace('導入と全編の掛け合いを改稿したv5。たこさんは中国うさぎ・ノーマルです。','完成稿v7。たこさんは中国うさぎ・ノーマルです。')
s+='\nモデル・サービスの出典\nSeedance / ByteDance: https://seed.bytedance.com/en/blog/seedance-2-0-official-launch\nWan / Alibaba: https://home.alibabagroup.com/en-US/ai-governance/wan\nMiniMax H3: https://www.minimax.io/news/minimax-h3-open-source\nHiggsfieldのプラン: https://higgsfield.ai/creator-hub/help-center/plans/how-do-higgsfield-plans-work\nRemotionの仕組み: https://www.remotion.dev/docs/idea\n'
p.write_text(s)
print('Adopted',len(items),'voices;',m['composition']['durationInFrames']/30,'seconds')
