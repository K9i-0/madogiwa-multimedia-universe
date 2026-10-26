#!/usr/bin/env python3
"""At 23:00 JST daily, publish one audited queued Short regardless of other posts.
Default is read-only preview. --execute enables the user-authorized routine.
Tokens/resumable URLs are never logged. Python 3.11+ standard library only.
"""
import argparse, datetime as dt, fcntl, hashlib, json, os, subprocess, sys
from contextlib import ExitStack
import urllib.request, urllib.parse, urllib.error
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2]
CONFIG=Path(__file__).with_name('config.json')
PRIVATE=Path.home()/'.config/mmu-youtube'
STATE=ROOT/'.local/shorts-nightly'
CREATORS=('k9i','sobaya')
EXTENDED_POLICY='studio-prompt-max101s-20261016'

def read(p):return json.loads(p.read_text())
def save(p,value):
 p.parent.mkdir(parents=True,exist_ok=True)
 temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');os.replace(temp,p)
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def timestamp(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00'))
def day_of(value,tz):return timestamp(value).astimezone(tz).date()
def eligible_time(now,c):return now.hour==c['hour'] and c['minute']<=now.minute<=c['lastAttemptMinute']
def public_today(videos,now):
 return [v for v in videos if v['status']['privacyStatus']=='public' and day_of(v['snippet']['publishedAt'],now.tzinfo)==now.date()]
def scheduled_today(videos,now):
 return [v for v in videos if v['status'].get('publishAt') and day_of(v['status']['publishAt'],now.tzinfo)==now.date() and timestamp(v['status']['publishAt'])>now]

class YouTube:
 def __init__(self,channel):
  self.channel=channel
  subprocess.run([sys.executable,str(ROOT/'16_MADOGIWA_STUDIO/youtube-auth/manage.py'),'access-token'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=45)
  self.token=read(PRIVATE/'access-token.json')['access_token']
 def get(self,resource,**params):
  url='https://www.googleapis.com/youtube/v3/'+resource+'?'+urllib.parse.urlencode(params)
  req=urllib.request.Request(url,headers={'Authorization':'Bearer '+self.token})
  try:
   with urllib.request.urlopen(req,timeout=45) as response:return json.load(response)
  except urllib.error.HTTPError as e:raise RuntimeError(f'YouTube HTTP {e.code}; no upload attempted by this read') from None
  except (urllib.error.URLError,TimeoutError):raise RuntimeError('YouTube connection failed; cannot verify duplicate uploads') from None
 def inventory(self):
  channels=self.get('channels',part='id,contentDetails',mine='true')['items']
  channel=next((x for x in channels if x['id']==self.channel),None)
  if not channel:raise RuntimeError('Authorized account does not own the configured channel')
  playlist=channel['contentDetails']['relatedPlaylists']['uploads'];ids=[];page=None
  while True:
   args=dict(part='contentDetails',playlistId=playlist,maxResults=50)
   if page:args['pageToken']=page
   response=self.get('playlistItems',**args);ids.extend(x['contentDetails']['videoId'] for x in response['items']);page=response.get('nextPageToken')
   if not page:break
  videos=[]
  for start in range(0,len(ids),50):videos.extend(self.get('videos',part='snippet,status,processingDetails',id=','.join(ids[start:start+50]))['items'])
  if any(v['snippet']['channelId']!=self.channel for v in videos):raise RuntimeError('Unexpected video channel')
  return videos
 def video(self,video_id):
  items=self.get('videos',part='snippet,status,processingDetails',id=video_id)['items']
  if len(items)!=1 or items[0]['snippet']['channelId']!=self.channel:raise RuntimeError('Uploaded video cannot be verified on expected channel')
  return items[0]

def creator(row):
 value=row.get('creator','k9i')
 if value not in CREATORS:raise RuntimeError('Unknown queue creator: '+str(value))
 return value

def queue_paths(c):
 paths=[ROOT/p for p in c.get('queues',[c['queue']])]
 if not paths or len(set(paths))!=len(paths):raise RuntimeError('Expected distinct configured queues')
 return paths

def load_queues(c):return [(q,read(q/'queue.json')) for q in queue_paths(c)]

def pending_queue(pending,c):
 # Pre-migration pending transfers belong to the original queue.
 q=ROOT/pending.get('queue',c['queue'])
 if q not in queue_paths(c):raise RuntimeError('Pending upload queue is no longer configured; restore it before resuming')
 return q

def eligible_candidates(queues,videos):
 titles={v['snippet']['title'].strip() for v in videos}
 posted_slugs=set();posted_originals=set()
 for q,rows in queues:
  for row in rows:
   if row.get('youtubeId') or row['status']=='published' or (q/'youtube_uploads'/f"{row['slug']}.json").exists():
    posted_slugs.add(row['slug'])
    if row.get('originalYoutubeId'):posted_originals.add(row['originalYoutubeId'])
 candidates=[];seen_slugs=set();seen_originals=set()
 for q,rows in queues:
  for row in sorted(rows,key=lambda r:r['order']):
   slug=row['slug'];original=row.get('originalYoutubeId')
   if row['status']!='ready' or slug in posted_slugs or slug in seen_slugs or (original and original in posted_originals|seen_originals):continue
   if read(q/row['metadata'])['snippet']['title'].strip() in titles:continue
   creator(row)
   candidates.append((q,row));seen_slugs.add(slug)
   if original:seen_originals.add(original)
 return candidates

def select_candidate(rows,videos,q):
 """Compatibility helper for the original single-queue selection."""
 candidates=eligible_candidates([(q,rows)],videos)
 return candidates[0][1] if candidates else None

def last_published_creator(queues,videos):
 """Use verified public channel IDs and successful receipts, never an attempted upload."""
 known={};history=[]
 for q,rows in queues:
  for row in rows:
   record=q/'youtube_uploads'/f"{row['slug']}.json"
   video_id=row.get('youtubeId')
   if record.exists():video_id=read(record).get('video_id',video_id)
   if video_id:known[video_id]=creator(row)
 for video in videos:
  if video['id'] not in known or video['status']['privacyStatus']!='public':continue
  if video.get('processingDetails',{}).get('processingStatus')!='succeeded' and video['status'].get('uploadStatus')!='processed':continue
  history.append((timestamp(video['snippet']['publishedAt']),known[video['id']]))
 for path in (STATE/'days').glob('*.json'):
  receipt=read(path)
  if receipt.get('phase')!='published':continue
  stamp=receipt.get('publishedAt',receipt['date']+'T23:00:00+09:00')
  history.append((timestamp(stamp),creator(receipt)))
 return max(history,key=lambda item:item[0])[1] if history else None

def publication_plan(queues,videos,last_creator=None,first_creator='k9i',limit=10):
 """Preview the same alternating order used by execution; no queue mutations."""
 if first_creator not in CREATORS:raise RuntimeError('Unknown first creator')
 remaining=eligible_candidates(queues,videos);plan=[]
 while remaining and len(plan)<limit:
  desired=next(c for c in CREATORS if c!=last_creator) if last_creator else first_creator
  index=next((i for i,(_,r) in enumerate(remaining) if creator(r)==desired),0)
  q,row=remaining.pop(index);plan.append((q,row));last_creator=creator(row)
 return plan

def validate(row,q):
 audits={v['slug']:v for v in read(q/'technical-audit.json')['videos']};visual={v['slug']:v for v in read(q/'visual-audit.json')['videos']}
 a=audits[row['slug']];v=visual[row['slug']];video=ROOT/row['output'];manifest=ROOT/row['manifest'];meta=q/row['metadata'];m=read(meta)
 if not a['passed'] or not v['passed'] or digest(video)!=a['sha256'] or v['sha256']!=a['sha256'] or digest(manifest)!=a['manifestSha256']:raise RuntimeError('Candidate is missing or differs from its approved audits: '+row['slug'])
 if m['status'].get('privacyStatus')!='public' or m['status'].get('publishAt'):raise RuntimeError('Expected immediate public metadata')
 duration=a['duration'];eligibility=row.get('eligibility')
 if eligibility:
  prompt=ROOT/eligibility.get('promptPath','')
  source_duration=eligibility.get('sourceDurationSeconds',0)
  if eligibility.get('policy')!=EXTENDED_POLICY or not 0<source_duration<=101 or not prompt.is_file() or not prompt.read_text().strip():raise RuntimeError('Candidate lacks the approved <=101s source and Studio prompt: '+row['slug'])
  allowed=0<duration<=101
 else:allowed=0<duration<60
 if not allowed or (a['width'],a['height'])!=(720,1280):raise RuntimeError('Candidate exceeds its approved duration or vertical size: '+row['slug'])
 return {'sha256':a['sha256'],'metadataSha256':digest(meta),'manifestSha256':a['manifestSha256']}

def confirm(api,pending,q):
 record=q/'youtube_uploads'/f"{pending['slug']}.json"
 if not record.exists():return False
 uploaded=read(record)
 if uploaded['sha256']!=pending['sha256']:raise RuntimeError('Upload record hash mismatch')
 video=api.video(uploaded['video_id']);status=video['status'];processing=video.get('processingDetails',{}).get('processingStatus')
 rows=read(q/'queue.json');row=next((r for r in rows if r['slug']==pending['slug']),None)
 if row is None:raise RuntimeError('Pending candidate was removed from its queue')
 pending.update(videoId=video['id'],url=uploaded['url'],privacyStatus=status['privacyStatus'],processingStatus=processing,creator=creator(row),queue=str(q.relative_to(ROOT)))
 if video.get('snippet',{}).get('publishedAt'):pending['publishedAt']=video['snippet']['publishedAt']
 pending['phase']='published' if status['privacyStatus']=='public' and processing=='succeeded' else 'awaiting_verification'
 save(STATE/'pending.json',pending)
 if pending['phase']!='published':return False
 for row in rows:
  if row['slug']==pending['slug']:row.update(status='published',youtubeId=video['id'])
 save(q/'queue.json',rows)
 save(STATE/'days'/f"{pending['date']}.json",pending)
 (STATE/'pending.json').unlink()
 return True

def run(execute=False):
 c=read(CONFIG);now=dt.datetime.now(ZoneInfo(c['timezone']));today=now.date().isoformat()
 if not c['enabled']:return {'action':'disabled'}
 if execute and not eligible_time(now,c):return {'action':'outside_window','time':now.isoformat()}
 if execute and (STATE/'days'/f'{today}.json').exists():return {'action':'already_completed_today','date':today}
 api=YouTube(c['channelId']);videos=api.inventory();posts=public_today(videos,now);scheduled=scheduled_today(videos,now)
 pending=read(STATE/'pending.json') if (STATE/'pending.json').exists() else None
 if pending:q=pending_queue(pending,c)
 if pending and execute:
  if confirm(api,pending,q):return {'action':'verified_previous_upload','slug':pending['slug'],'url':pending['url']}
  if pending.get('videoId'):return {'action':'awaiting_verification','videoId':pending['videoId'],'privacyStatus':pending['privacyStatus'],'processingStatus':pending['processingStatus']}
  if pending['date']!=today:raise RuntimeError('Earlier unresolved upload needs review; no new upload will be created')
  # If response/record was lost but video appears, reconcile the same ID, never start another.
  matches=[v for v in videos if v['snippet']['title']==pending['title']]
  if matches:raise RuntimeError('Pending title already exists on channel without a local result record; review before resuming')
 queues=load_queues(c);last_creator=last_published_creator(queues,videos)
 if pending:
  row=next((r for queue,rows in queues if queue==q for r in rows if r['slug']==pending['slug']),None)
  if not row:raise RuntimeError('Pending candidate was removed from its queue')
 else:
  plan=publication_plan(queues,videos,last_creator,c.get('firstCreator','k9i'),limit=1)
  q,row=plan[0] if plan else (None,None)
 if not row:return {'action':'queue_empty','date':today}
 checked=validate(row,q)
 if pending and any(pending[k]!=checked[k] for k in checked):raise RuntimeError('Pending upload inputs changed; do not resume automatically')
 result={'action':'would_publish','date':today,'title':read(q/row['metadata'])['snippet']['title'],'slug':row['slug'],'output':row['output'],'queue':str(q.relative_to(ROOT)),'creator':creator(row),'lastPublishedCreator':last_creator,'publicCount':len(posts),'scheduledCount':len(scheduled),'channelInventoryCount':len(videos)}
 if not execute:return result
 # Recheck the time window and candidate duplication immediately before upload.
 now=dt.datetime.now(ZoneInfo(c['timezone']))
 if now.date().isoformat()!=today or not eligible_time(now,c):return {'action':'window_closed'}
 latest=api.inventory()
 if any(v['snippet']['title']==result['title'] for v in latest):return {'action':'candidate_already_on_channel'}
 if validate(row,q)!=checked:raise RuntimeError('Inputs changed during validation')
 pending={**result,**checked,'phase':'uploading'};save(STATE/'pending.json',pending)
 record=q/'youtube_uploads'/f"{row['slug']}.json"
 # Common lock is held by main; uploader privately resumes by file SHA on retries.
 completed=subprocess.run([sys.executable,str(ROOT/'16_MADOGIWA_STUDIO/tools/upload-youtube.py'),str(ROOT/row['output']),'--metadata',str(q/row['metadata']),'--record',str(record)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=420)
 if completed.returncode:raise RuntimeError('Upload did not complete. Private resumable session retained; same candidate only on retry')
 confirmed=confirm(api,pending,q)
 return {'action':'published' if confirmed else 'uploaded_processing','slug':row['slug'],'videoId':pending.get('videoId'),'url':pending.get('url')}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');args=p.parse_args();c=read(CONFIG);STATE.mkdir(parents=True,exist_ok=True)
 with ExitStack() as stack:
  try:
   # One process-wide lock plus every configured queue's existing batch-upload lock.
   paths=[STATE/'upload.lock']
   for q in sorted(queue_paths(c)):
    (q/'youtube_uploads').mkdir(exist_ok=True);paths.append(q/'youtube_uploads/.lock')
   for path in paths:
    lock=stack.enter_context(path.open('a'));fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:print('{"action":"another_upload_running"}');return
  try:result=run(args.execute)
  except Exception as e:
   # Do not print traceback or HTTP URLs / token-bearing subprocess output.
   result={'action':'error','error':str(e) if isinstance(e,RuntimeError) else type(e).__name__}
  result['checkedAt']=dt.datetime.now(dt.timezone.utc).isoformat();print(json.dumps(result,ensure_ascii=False),flush=True)
  save(STATE/('last-run.json' if args.execute else 'last-preview.json'),result)
  if result['action']=='error':raise SystemExit(1)
if __name__=='__main__':main()
