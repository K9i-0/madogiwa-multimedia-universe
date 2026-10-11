#!/usr/bin/env python3
"""Refresh local metadata and review page; never upload or alter existing upload records."""
from pathlib import Path
import json,html,os
Q=Path(__file__).resolve().parent;R=Q.parents[1]
def main():
 rows=json.loads((Q/'queue.json').read_text())
 cache=Q/'out/youtube-sources.json'
 source={r['id']:r for r in json.loads(cache.read_text())} if cache.exists() else {}
 meta=Q/'metadata';meta.mkdir(exist_ok=True)
 sections=[]
 for r in rows:
  existing=meta/f"{r['order']:02d}-{r['slug']}.json"
  if r['originalYoutubeId'] not in source and not existing.exists():raise SystemExit('Missing original metadata/credits: '+r['slug'])
  old=source.get(r['originalYoutubeId'],{}).get('snippet',{});m=json.loads((R/r['manifest']).read_text())
  description=f"{r['title']}\n\n窓際族物語の縦版ショート。\n横版：https://youtu.be/{r['originalYoutubeId']}\n\n"
  prior=old.get('description','').strip()
  if prior:description+=prior+'\n\n'
  else:description+='窓際族物語 公式サイト\nhttps://madogiwa.work\n\n'
  if r['slug']=='madogiwa-ojousama-club':
   description+=(R/'03_SCRIPTS/87_mado_kizoku/music_credit.txt').read_text()+'\nVOICEVOX:Voidoll(CV:丹下桜)\n\n'
  description+='#窓際族物語 #Shorts'
  assert len(description.encode('utf-8'))<=5000,(r['slug'],'description too long')
  md={'snippet':{'title':r['title']+' #Shorts','description':description,'categoryId':'23','tags':['窓際族物語','Shorts'],'defaultLanguage':'ja'},'status':{'privacyStatus':'public','selfDeclaredMadeForKids':False,'containsSyntheticMedia':True,'embeddable':True}}
  dest=meta/f"{r['order']:02d}-{r['slug']}.json";r['metadata']=str(dest.relative_to(Q))
  if dest.exists():md=json.loads(dest.read_text()) # Keep reviewed text, including credits, without an ignored source cache.
  dest.write_text(json.dumps(md,ensure_ascii=False,indent=2)+'\n')
  video=os.path.relpath(R/r['output'],Q);poster='remotion/out/'+r['slug']+'.png'
  sections.append(f'''<article data-batch="{r['batch']}"><h2><small>次回から第{r['batch']}週 · {r['order']:02d}</small>{html.escape(r['title'])}</h2><video controls preload="none" poster="{poster}" src="{video}"></video><p>{m['durationInFrames']/m['fps']:.2f}秒 · 720×1280 · {m['fps']:g}fps</p><a href="{video}">完成MP4</a> · <a href="{r['metadata']}">投稿文</a> · <a href="https://youtu.be/{r['originalYoutubeId']}">横版</a></article>''')
 (Q/'queue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 page='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Shorts投稿待ち37本</title><style>body{margin:0;background:#101820;color:#edf1f4;font:16px system-ui}header{padding:28px;position:sticky;top:0;background:#101820ef;z-index:1}h1{margin:0 0 10px}p{color:#b9c9d5}select{font:inherit;padding:8px;background:#243341;color:white;border-radius:6px}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:24px;padding:24px}article{background:#1b2934;border-radius:12px;padding:16px}h2{font-size:20px;min-height:64px}small{display:block;color:#a9c1d2;font-size:13px;margin-bottom:8px}video{width:100%;max-height:640px;background:black}a{color:#a8d5ff}article[hidden]{display:none}</style><header><h1>Shorts投稿待ち37本</h1><p>ローカル制作・1分未満。投稿済み5本は除外。次回から5本×7週＋2本（8週分）。日付予約・新規投稿は未実施。</p><label>表示：<select id="batch"><option value="">全37本</option>'''+''.join(f'<option value="{n}">第{n}週（{5 if n<8 else 2}本）</option>' for n in range(1,9))+'''</select></label></header><main>'''+''.join(sections)+'''</main><script>document.querySelector('#batch').addEventListener('change',e=>{for(const a of document.querySelectorAll('article'))a.hidden=!!e.target.value&&a.dataset.batch!==e.target.value;});</script></html>'''
 (Q/'review.html').write_text(page)
 print('Prepared metadata and review for',len(rows))
if __name__=='__main__':main()
