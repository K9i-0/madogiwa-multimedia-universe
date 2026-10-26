import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import subprocess
import colab_h3 as app

class ColabTests(unittest.TestCase):
    def test_lifecycle_and_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); wf=d/'workflow.json';job=d/'job'
            wf.write_text(json.dumps({'1':{'class_type':'MiniMaxH3ImageToVideo','inputs':{'width':864,'height':480,'length':124}}}))
            app.prepare(wf,job)
            calls=[]
            def fake(*args,**kw):
                calls.append(args)
                if args[0]=='download':
                    with zipfile.ZipFile(args[-1],'w') as z:
                        z.writestr('video_480p.mp4',b'recovery-fixture')
                        z.writestr('status.json',json.dumps({'status':'complete','sha256':{'video_480p.mp4':hashlib.sha256(b'recovery-fixture').hexdigest()}}))
            argv=['colab_h3','run','--job',str(job),'--session','h3-test']
            with patch('sys.argv',argv),patch.object(app,'cli',fake),patch.object(app.shutil,'which',return_value='/bin/colab'):
                app.main()
            self.assertEqual([c[0] for c in calls],['new','upload','exec','download','stop'])
            self.assertEqual(json.loads((job/'job.json').read_text())['status'],'stopped')
            # A lost exec connection leaves the same session alive; resuming must not allocate again.
            state=json.loads((job/'job.json').read_text());state['status']='running';app.save(job/'job.json',state)
            def broken(*args,**kw):
                calls.append(args)
                if args[0]=='exec':raise subprocess.CalledProcessError(1,['colab','exec'])
            calls.clear()
            with patch('sys.argv',argv),patch.object(app,'cli',broken),patch.object(app.shutil,'which',return_value='/bin/colab'):
                with self.assertRaises(subprocess.CalledProcessError):app.main()
            self.assertEqual([c[0] for c in calls],['upload','exec'])
            calls.clear()
            with patch('sys.argv',argv),patch.object(app,'cli',fake),patch.object(app.shutil,'which',return_value='/bin/colab'):
                app.main()
            self.assertEqual([c[0] for c in calls],['upload','exec','download','stop'])

    def test_input_paths(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);wf=d/'workflow.json'
            wf.write_text(json.dumps({'1':{'class_type':'MiniMaxH3ImageToVideo','inputs':{}},'2':{'class_type':'LoadImage','inputs':{'image':'../private.png'}}}))
            with self.assertRaises(ValueError):app.prepare(wf,d/'job')
            self.assertFalse((d/'job').exists())

if __name__=='__main__':unittest.main()
