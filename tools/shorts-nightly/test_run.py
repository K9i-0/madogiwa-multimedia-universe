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
 def test_later_same_day_schedule_prevents_filler(self):
  now=dt.datetime(2026,10,15,23,tzinfo=JST)
  v=video('2026-10-10T00:00:00Z','private',schedule='2026-10-15T14:30:00Z')
  self.assertEqual(m.scheduled_today([v],now),[v])
  v['status']['publishAt']='2026-10-15T15:00:00Z'
  self.assertEqual(m.scheduled_today([v],now),[])
 def test_wake_after_midnight_does_not_upload(self):
  c={'hour':23,'minute':0,'lastAttemptMinute':50}
  for hour,minute,expected in [(22,59,False),(23,0,True),(23,50,True),(23,51,False),(0,1,False)]:
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
   class API:
    def video(self,_):return {'id':'id','status':{'privacyStatus':'public'},'processingDetails':{'processingStatus':'processing'}}
   pending=dict(slug='x',sha256='s',date='2026-10-15')
   with patch.object(m,'STATE',state):
    self.assertFalse(m.confirm(API(),pending,q));self.assertEqual(pending['phase'],'awaiting_verification');self.assertTrue((state/'pending.json').exists())
 def test_success_marks_queue_and_daily_receipt(self):
  with tempfile.TemporaryDirectory() as d:
   q=Path(d)/'q';state=Path(d)/'state';m.save(q/'youtube_uploads/x.json',{'sha256':'s','video_id':'id','url':'https://youtu.be/id'})
   m.save(q/'queue.json',[{'slug':'x','status':'ready'}]);pending=dict(slug='x',sha256='s',date='2026-10-15');m.save(state/'pending.json',pending)
   class API:
    def video(self,_):return {'id':'id','status':{'privacyStatus':'public'},'processingDetails':{'processingStatus':'succeeded'}}
   with patch.object(m,'STATE',state):
    self.assertTrue(m.confirm(API(),pending,q));self.assertFalse((state/'pending.json').exists());self.assertTrue((state/'days/2026-10-15.json').exists());self.assertEqual(m.read(q/'queue.json')[0]['status'],'published')
 def test_completed_day_never_uploads_again(self):
  class FixedDateTime(dt.datetime):
   @classmethod
   def now(cls,tz=None):return cls(2026,10,15,23,20,tzinfo=JST)
  with tempfile.TemporaryDirectory() as d:
   state=Path(d);m.save(state/'days/2026-10-15.json',{'phase':'published'})
   with patch.object(m,'STATE',state),patch.object(m.dt,'datetime',FixedDateTime),patch.object(m,'YouTube') as api:
    self.assertEqual(m.run(True)['action'],'already_completed_today');api.assert_not_called()
 def test_api_failure_cannot_become_zero_posts(self):
  with patch.object(m,'YouTube',side_effect=RuntimeError('network unavailable')):
   with self.assertRaises(RuntimeError):m.run(False)
if __name__=='__main__':unittest.main()
