import datetime as dt
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
spec=importlib.util.spec_from_file_location('nightly',Path(__file__).with_name('run.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
JST=ZoneInfo('Asia/Tokyo')
def video(stamp,privacy='public',title='Example',schedule=None):
 v={'id':'example','snippet':{'publishedAt':stamp,'title':title},'status':{'privacyStatus':privacy}}
 if schedule:v['status']['publishAt']=schedule
 return v
class NightlyTest(unittest.TestCase):
 def test_jst_day_boundary(self):
  now=dt.datetime(2026,10,15,23,tzinfo=JST)
  vs=[video('2026-10-14T14:59:59Z'),video('2026-10-14T15:00:00Z'),video('2026-10-15T14:00:00Z'),video('2026-10-14T16:00:00Z','private'),video('2026-10-14T16:00:00Z','unlisted')]
  self.assertEqual(m.public_today(vs,now),vs[1:3])
 def test_later_same_day_schedule_is_counted_for_diagnostics(self):
  now=dt.datetime(2026,10,15,23,tzinfo=JST)
  v=video('2026-10-10T00:00:00Z','private',schedule='2026-10-15T14:30:00Z')
  self.assertEqual(m.scheduled_today([v],now),[v])
  v['status']['publishAt']='2026-10-15T15:00:00Z'
  self.assertEqual(m.scheduled_today([v],now),[])
 def test_wake_after_midnight_does_not_upload(self):
  c={'hour':18,'minute':0,'lastAttemptMinute':50}
  for hour,minute,expected in [(17,59,False),(18,0,True),(18,50,True),(18,51,False),(23,0,False),(0,1,False)]:
   self.assertEqual(m.eligible_time(dt.datetime(2026,10,15,hour,minute,tzinfo=JST),c),expected)
 def test_selection_skips_published_record_and_remote_title(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d);(q/'youtube_uploads').mkdir();rows=[]
   for i in range(1,5):
    m.save(q/f'{i}.json',{'snippet':{'title':f'Short {i}'}});rows.append(dict(order=i,slug=str(i),status='ready',metadata=f'{i}.json'))
   rows[0]['status']='published';m.save(q/'youtube_uploads/2.json',{'video_id':'existing'})
   self.assertEqual(m.select_candidate(rows,[video('2026-10-01T00:00:00Z',title='Short 3')],q)['slug'],'4')
 def test_changed_video_blocks_upload(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);q=root/'q';q.mkdir();p=root/'video.mp4';p.write_bytes(b'adopted');man=root/'manifest.json';man.write_text('{}');m.save(q/'meta.json',{'status':{'privacyStatus':'public'}})
   row=dict(slug='x',output='video.mp4',manifest='manifest.json',metadata='meta.json')
   a=dict(slug='x',passed=True,sha256=m.digest(p),manifestSha256=m.digest(man),duration=20,width=720,height=1280)
   m.save(q/'technical-audit.json',{'videos':[a]});m.save(q/'visual-audit.json',{'videos':[a]})
   with patch.object(m,'ROOT',root):
    m.validate(row,q);p.write_bytes(b'changed')
    with self.assertRaises(RuntimeError):m.validate(row,q)
 def test_processing_does_not_mark_published(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/'q';state=Path(d)/'state';m.save(q/'youtube_uploads/x.json',{'sha256':'s','video_id':'id','url':'https://youtu.be/id'})
   m.save(q/'queue.json',[{'slug':'x','status':'ready'}])
   class API:
    def video(self,_):return {'id':'id','status':{'privacyStatus':'public'},'processingDetails':{'processingStatus':'processing'}}
   pending=dict(slug='x',sha256='s',date='2026-10-15')
   with patch.object(m,'STATE',state),patch.object(m,'ROOT',Path(d)):
    self.assertFalse(m.confirm(API(),pending,q));self.assertEqual(pending['phase'],'awaiting_verification');self.assertTrue((state/'pending.json').exists())
 def test_success_marks_queue_and_daily_receipt(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/'q';state=Path(d)/'state';m.save(q/'youtube_uploads/x.json',{'sha256':'s','video_id':'id','url':'https://youtu.be/id'})
   m.save(q/'queue.json',[{'slug':'x','status':'ready'}]);pending=dict(slug='x',sha256='s',date='2026-10-15');m.save(state/'pending.json',pending)
   class API:
    def video(self,_):return {'id':'id','status':{'privacyStatus':'public'},'processingDetails':{'processingStatus':'succeeded'}}
   with patch.object(m,'STATE',state),patch.object(m,'ROOT',Path(d)):
    self.assertTrue(m.confirm(API(),pending,q));self.assertFalse((state/'pending.json').exists());self.assertTrue((state/'days/2026-10-15.json').exists());self.assertEqual(m.read(q/'queue.json')[0]['status'],'published')
 def test_completed_day_never_uploads_again(self):
  class FixedDateTime(dt.datetime):
   @classmethod
   def now(cls,tz=None):return cls(2026,10,15,18,20,tzinfo=JST)
  with tempfile.TemporaryDirectory() as d:
   state=Path(d);m.save(state/'days/2026-10-15.json',{'phase':'published'})
   with patch.object(m,'STATE',state),patch.object(m.dt,'datetime',FixedDateTime),patch.object(m,'YouTube') as api:
    self.assertEqual(m.run(True)['action'],'already_completed_today');api.assert_not_called()
 def test_api_failure_blocks_unverified_upload(self):
  with patch.object(m,'YouTube',side_effect=RuntimeError('network unavailable')):
   with self.assertRaises(RuntimeError):m.run(False)

class DailyPostingTest(unittest.TestCase):
 def test_other_posts_and_schedules_do_not_block_but_duplicates_do(self):
  class FixedDateTime(dt.datetime):
   @classmethod
   def now(cls,tz=None):return cls(2026,10,26,18,0,tzinfo=JST)
  public=video('2026-10-26T08:00:00Z')
  scheduled=video('2026-10-25T00:00:00Z','private',schedule='2026-10-26T09:30:00Z')
  duplicate=video('2026-10-26T09:00:00Z',title='Queued Short')
  cases=[('public',[public],[public],True),('scheduled',[scheduled],[scheduled],True),('late-public',[],[public],True),('late-scheduled',[],[scheduled],True),('late-duplicate',[],[duplicate],False)]
  for name,initial,latest,should_upload in cases:
   with self.subTest(name=name),tempfile.TemporaryDirectory() as d:
    root=Path(d);q=root/'queue';state=root/'state';config=root/'config.json'
    m.save(config,{'enabled':True,'timezone':'Asia/Tokyo','hour':18,'minute':0,'lastAttemptMinute':50,'channelId':'channel','queue':'queue'})
    m.save(q/'queue.json',[{'order':1,'slug':'short','status':'ready','metadata':'meta.json','output':'short.mp4'}])
    m.save(q/'meta.json',{'snippet':{'title':'Queued Short'}})
    checked={'sha256':'hash','metadataSha256':'meta','manifestSha256':'manifest'}
    def finish_upload(*args,**kwargs):
     m.save(q/'youtube_uploads/short.json',{'sha256':'hash','video_id':'new-id','url':'https://youtu.be/new-id'})
     return m.subprocess.CompletedProcess(args[0],0)
    with patch.object(m,'ROOT',root),patch.object(m,'STATE',state),patch.object(m,'CONFIG',config),patch.object(m.dt,'datetime',FixedDateTime),patch.object(m,'YouTube') as api_factory,patch.object(m,'validate',return_value=checked),patch.object(m.subprocess,'run',side_effect=finish_upload) as upload:
     api=api_factory.return_value
     api.inventory.return_value=initial
     preview=m.run(False)
     self.assertEqual(preview['action'],'would_publish')
     self.assertEqual(preview['publicCount'],len(m.public_today(initial,FixedDateTime.now())))
     self.assertEqual(preview['scheduledCount'],len(m.scheduled_today(initial,FixedDateTime.now())))
     upload.assert_not_called()
     api.inventory.side_effect=[initial,latest]
     api.video.return_value={'id':'new-id','snippet':{'publishedAt':'2026-10-26T09:00:00Z'},'status':{'privacyStatus':'public'},'processingDetails':{'processingStatus':'succeeded'}}
     result=m.run(True)
     if should_upload:
      self.assertEqual(result['action'],'published');upload.assert_called_once()
      self.assertTrue((state/'days/2026-10-26.json').exists())
      self.assertEqual(m.run(True)['action'],'already_completed_today');upload.assert_called_once()
     else:
      self.assertEqual(result['action'],'candidate_already_on_channel');upload.assert_not_called()
      self.assertFalse((state/'pending.json').exists())

class AlternatingQueueTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.root_patch=patch.object(m,'ROOT',self.root);self.root_patch.start()
  self.state_patch=patch.object(m,'STATE',self.root/'state');self.state_patch.start()
  self.config={'queue':'old','queues':['old','new'],'firstCreator':'sobaya'}
  self.queues=[]
  for name,author in [('old','k9i'),('new','sobaya')]:
   q=self.root/name;rows=[]
   for i in range(1,4):
    row={'order':i,'slug':f'{name}-{i}','status':'ready','metadata':f'{i}.json','originalYoutubeId':f'original-{name}-{i}'}
    if author=='sobaya':row['creator']=author
    rows.append(row);m.save(q/f'{i}.json',{'snippet':{'title':f'{name} short {i}'}})
   m.save(q/'queue.json',rows);self.queues.append((q,rows))
 def tearDown(self):
  self.state_patch.stop();self.root_patch.stop();self.temp.cleanup()
 def slugs(self,**kwargs):
  return [r['slug'] for _,r in m.publication_plan(self.queues,[],**kwargs)]
 def test_alternates_from_last_success_and_keeps_each_creator_order(self):
  self.assertEqual(self.slugs(last_creator='k9i'),['new-1','old-1','new-2','old-2','new-3','old-3'])
  self.assertEqual(self.slugs(last_creator='sobaya',limit=2),['old-1','new-1'])
 def test_initial_creator_is_used_only_without_history(self):
  self.assertEqual(self.slugs(first_creator='sobaya',limit=1),['new-1'])
  self.assertEqual(self.slugs(last_creator='sobaya',first_creator='sobaya',limit=1),['old-1'])
 def test_exhausted_creator_does_not_block_other_ready_work(self):
  for row in self.queues[1][1]:row['status']='rendering'
  self.assertEqual(self.slugs(last_creator='k9i'),['old-1','old-2','old-3'])
 def test_record_in_other_queue_blocks_duplicate_original(self):
  self.queues[1][1][0]['originalYoutubeId']='original-old-1'
  m.save(self.queues[0][0]/'youtube_uploads/old-1.json',{'video_id':'id'})
  self.assertEqual(self.slugs(last_creator='k9i',limit=2),['new-2','old-2'])
 def test_duplicate_unposted_slug_or_original_is_only_selected_once(self):
  self.queues[1][1][0]['originalYoutubeId']='original-old-1'
  self.queues[1][1][1]['slug']='old-2'
  self.assertEqual(self.slugs(last_creator='k9i'),['new-3','old-1','old-2','old-3'])
 def test_creator_is_not_inferred_from_character_in_title(self):
  self.assertEqual(m.creator({'title':'そば屋'}),'k9i')
  with self.assertRaises(RuntimeError):m.creator({'creator':'unknown'})
 def test_last_success_uses_channel_publication_time_and_processing(self):
  old=self.queues[0][1][0];new=self.queues[1][1][0]
  old['youtubeId']='a';new['youtubeId']='b'
  a=video('2026-10-15T14:00:00Z');a.update(id='a',processingDetails={'processingStatus':'succeeded'})
  b=video('2026-10-16T14:00:00Z');b.update(id='b',processingDetails={'processingStatus':'processing'})
  self.assertEqual(m.last_published_creator(self.queues,[a,b]),'k9i')
  b['processingDetails']['processingStatus']='succeeded'
  self.assertEqual(m.last_published_creator(self.queues,[a,b]),'sobaya')
  b['status']['privacyStatus']='private'
  self.assertEqual(m.last_published_creator(self.queues,[a,b]),'k9i')
 def test_old_upload_record_identifies_creator_without_changing_record(self):
  record=self.queues[1][0]/'youtube_uploads/new-1.json'
  m.save(record,{'video_id':'b','sha256':'immutable'});original=record.read_bytes()
  b=video('2026-10-16T14:00:00Z');b.update(id='b');b['status']['uploadStatus']='processed'
  self.assertEqual(m.last_published_creator(self.queues,[b]),'sobaya')
  self.assertEqual(record.read_bytes(),original)
 def test_successful_receipts_persist_alternation_after_remote_privacy_changes(self):
  m.save(m.STATE/'days/2026-10-15.json',{'phase':'published','date':'2026-10-15','creator':'sobaya'})
  m.save(m.STATE/'days/2026-10-16.json',{'phase':'awaiting_verification','date':'2026-10-16','creator':'k9i'})
  self.assertEqual(m.last_published_creator(self.queues,[]),'sobaya')
 def test_pending_keeps_its_queue_across_config_migration(self):
  self.assertEqual(m.pending_queue({'slug':'old-1'},self.config),self.root/'old')
  self.assertEqual(m.pending_queue({'slug':'new-1','queue':'new'},self.config),self.root/'new')
  with self.assertRaises(RuntimeError):m.pending_queue({'queue':'removed'},self.config)
 def test_confirm_updates_only_new_queue_and_records_creator(self):
  q=self.queues[1][0];old_bytes=(self.queues[0][0]/'queue.json').read_bytes()
  m.save(q/'youtube_uploads/new-1.json',{'sha256':'s','video_id':'b','url':'https://youtu.be/b'})
  pending={'slug':'new-1','sha256':'s','date':'2026-10-16','queue':'new','creator':'sobaya'}
  m.save(m.STATE/'pending.json',pending)
  class API:
   def video(self,_):return {'id':'b','status':{'privacyStatus':'public'},'processingDetails':{'processingStatus':'succeeded'},'snippet':{'publishedAt':'2026-10-16T14:01:00Z'}}
  self.assertTrue(m.confirm(API(),pending,q))
  self.assertEqual((self.queues[0][0]/'queue.json').read_bytes(),old_bytes)
  self.assertEqual(m.read(q/'queue.json')[0]['youtubeId'],'b')
  receipt=m.read(m.STATE/'days/2026-10-16.json')
  self.assertEqual(receipt['creator'],'sobaya');self.assertEqual(receipt['queue'],'new')
  self.assertEqual(receipt['publishedAt'],'2026-10-16T14:01:00Z')
 def test_preview_keeps_pending_candidate_even_when_opposite_creator_is_due(self):
  config_path=self.root/'config.json'
  m.save(config_path,{**self.config,'timezone':'Asia/Tokyo','enabled':True,'channelId':'channel'})
  checked={'sha256':'same','metadataSha256':'meta','manifestSha256':'manifest'}
  for q,rows in self.queues:
   for row in rows:row['output']=row['slug']+'.mp4'
   m.save(q/'queue.json',rows)
  class API:
   def __init__(self,_):pass
   def inventory(self):return []
  with patch.object(m,'CONFIG',config_path),patch.object(m,'YouTube',API),patch.object(m,'validate',return_value=checked),patch.object(m.subprocess,'run') as upload:
   for saved_queue,slug,expected_creator in [(None,'old-2','k9i'),('new','new-2','sobaya')]:
    pending={'slug':slug,'date':dt.datetime.now(JST).date().isoformat(),**checked}
    if saved_queue:pending['queue']=saved_queue
    m.save(m.STATE/'pending.json',pending)
    result=m.run(False)
    self.assertEqual(result['slug'],slug);self.assertEqual(result['creator'],expected_creator)
   upload.assert_not_called()
 def test_batch_lock_in_either_queue_blocks_nightly(self):
  config_path=self.root/'config.json';m.save(config_path,self.config)
  for q,_ in self.queues:
   (q/'youtube_uploads').mkdir(exist_ok=True)
   with (q/'youtube_uploads/.lock').open('a') as busy:
    m.fcntl.flock(busy,m.fcntl.LOCK_EX|m.fcntl.LOCK_NB)
    with patch.object(m,'CONFIG',config_path),patch.object(m.sys,'argv',['run.py']),patch.object(m,'run') as run,patch('builtins.print') as output:
     m.main();run.assert_not_called();output.assert_called_once_with('{"action":"another_upload_running"}')

class ExtendedDurationTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.q=self.root/'q'
  self.root_patch=patch.object(m,'ROOT',self.root);self.root_patch.start()
  (self.root/'video.mp4').write_bytes(b'adopted');(self.root/'manifest.json').write_text('{}')
  (self.root/'studio-prompt.txt').write_text('Speaker: example dialogue')
  m.save(self.q/'meta.json',{'status':{'privacyStatus':'public'}})
  self.row={'slug':'x','output':'video.mp4','manifest':'manifest.json','metadata':'meta.json'}
  self.audit={'slug':'x','passed':True,'sha256':m.digest(self.root/'video.mp4'),'manifestSha256':m.digest(self.root/'manifest.json'),'duration':101,'width':720,'height':1280}
  self.write_audits()
 def write_audits(self):
  m.save(self.q/'technical-audit.json',{'videos':[self.audit]});m.save(self.q/'visual-audit.json',{'videos':[self.audit]})
 def approve(self):
  self.row['eligibility']={'policy':m.EXTENDED_POLICY,'sourceDurationSeconds':101,'promptPath':'studio-prompt.txt'}
 def tearDown(self):self.root_patch.stop();self.temp.cleanup()
 def test_existing_rows_keep_strict_subminute_limit(self):
  with self.assertRaises(RuntimeError):m.validate(self.row,self.q)
  self.audit['duration']=60;self.write_audits()
  with self.assertRaises(RuntimeError):m.validate(self.row,self.q)
  self.audit['duration']=59.99;self.write_audits();m.validate(self.row,self.q)
 def test_approved_101_seconds_with_studio_prompt_is_allowed(self):
  self.approve();m.validate(self.row,self.q)
 def test_over_limit_source_or_output_is_rejected(self):
  self.approve();self.row['eligibility']['sourceDurationSeconds']=101.01
  with self.assertRaises(RuntimeError):m.validate(self.row,self.q)
  self.approve();self.audit['duration']=101.01;self.write_audits()
  with self.assertRaises(RuntimeError):m.validate(self.row,self.q)
 def test_missing_or_empty_prompt_is_rejected_even_for_short_output(self):
  self.approve();self.audit['duration']=30;self.write_audits()
  (self.root/'studio-prompt.txt').write_text(' ')
  with self.assertRaises(RuntimeError):m.validate(self.row,self.q)
  (self.root/'studio-prompt.txt').unlink()
  with self.assertRaises(RuntimeError):m.validate(self.row,self.q)
 def test_unrecognized_approval_policy_is_rejected(self):
  self.approve();self.row['eligibility']['policy']='anything-longer'
  with self.assertRaises(RuntimeError):m.validate(self.row,self.q)
if __name__=='__main__':unittest.main()
