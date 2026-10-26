"""Offline contract tests; a synthetic MP4 is NOT evidence of H3 inference."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = Path(__file__).resolve().parent


class WorkflowTests(unittest.TestCase):
    def test_graph_and_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            (d/'prompt.txt').write_text('A cup with rising steam.')
            base = [sys.executable, str(HERE/'build_workflow.py'), '--prompt-file', str(d/'prompt.txt'),
                    '--out', str(d/'graph.json'), '--frames', '124']
            subprocess.run(base + ['--mode', 't2v', '--turbo'], check=True, capture_output=True)
            g = json.loads((d/'graph.json').read_text())
            self.assertEqual(g['136']['inputs']['height'], 480)
            self.assertEqual(g['124']['inputs']['steps'], 8)
            self.assertEqual(g['126']['inputs']['model'], ['150', 0])
            subprocess.run(base + ['--mode', 'r2v', '--image', 'person.png', '--audio', 'voice.wav'],
                           check=True, capture_output=True)
            g = json.loads((d/'graph.json').read_text())
            self.assertEqual(g['136']['inputs']['ref_images.ref_image_0'], ['200', 0])
            self.assertEqual(g['136']['inputs']['ref_audios.ref_audio_0'], ['201', 0])
            for extra in [['--mode', 't2v', '--frames', '-12'],
                          ['--mode', 't2v', '--width', '854'],
                          ['--mode', 'r2v'], ['--mode', 'i2v']]:
                self.assertNotEqual(subprocess.run(base + extra, capture_output=True).returncode, 0)

    def test_download_resume_and_failed_generation(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=blue:s=864x480:r=24',
                            '-f', 'lavfi', '-i', 'anullsrc=r=32000:cl=stereo', '-frames:v', '124',
                            '-shortest', '-c:v', 'libx264', '-preset', 'ultrafast', '-c:a', 'aac',
                            str(d/'fixture.mp4')], check=True)
            media = (d/'fixture.mp4').read_bytes()
            shared = {'posts': 0, 'fail': False}
            class Handler(BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass
                def respond(self, value):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(value if isinstance(value, bytes) else json.dumps(value).encode())
                def do_POST(self):
                    self.rfile.read(int(self.headers['Content-Length']))
                    shared['posts'] += 1
                    self.respond({'prompt_id': 'job1'})
                def do_GET(self):
                    if self.path.startswith('/history/'):
                        self.respond({'job1': {'status': {'completed': True,
                            'status_str': 'error' if shared['fail'] else 'success', 'messages': []},
                            'outputs': {'92': {'videos': [{'filename': 'fixture.mp4'}]}}}})
                    elif self.path.startswith('/view?'):
                        self.respond(media)
                    else:
                        self.respond({})
            server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                (d/'g.json').write_text(json.dumps({'136': {'class_type': 'MiniMaxH3ImageToVideo',
                    'inputs': {'width': 864, 'height': 480, 'length': 124}}}))
                cmd = [sys.executable, str(HERE/'run_workflow.py'), str(d/'g.json'), '--out', str(d/'out.mp4'),
                       '--server', f'http://127.0.0.1:{server.server_port}', '--poll', '0.01']
                subprocess.run(cmd, check=True, capture_output=True)
                self.assertEqual(json.loads((d/'out.job.json').read_text())['status'], 'verified')
                subprocess.run(cmd, check=True, capture_output=True)
                self.assertEqual(shared['posts'], 1)
                # Resume an interrupted download from the existing job; never POST again.
                (d/'out.mp4').unlink()
                subprocess.run(cmd, check=True, capture_output=True)
                self.assertEqual(shared['posts'], 1)
                shared['fail'] = True
                failed = cmd.copy()
                failed[failed.index('--out')+1] = str(d/'failed.mp4')
                self.assertNotEqual(subprocess.run(failed, capture_output=True).returncode, 0)
                self.assertFalse((d/'failed.mp4').exists())
            finally:
                server.shutdown()
                server.server_close()


if __name__ == '__main__':
    unittest.main()
