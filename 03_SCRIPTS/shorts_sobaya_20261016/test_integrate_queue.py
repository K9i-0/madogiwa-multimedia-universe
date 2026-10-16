#!/usr/bin/env python3
"""Fail-closed checks for the one-time batch queue integration."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('integration', Path(__file__).with_name('integrate_queue.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.q = self.root / 'batch'
        self.q.mkdir()
        self.patchers = [patch.object(m, 'ROOT', self.root), patch.object(m, 'Q', self.q),
                         patch.object(m, 'source_duration', return_value=30.16)]
        for item in self.patchers:
            item.start()
            self.addCleanup(item.stop)
        for group, count in zip(m.GROUPS, (11, 11, 2, 10)):
            rows, audits = [], []
            for index in range(count):
                slug = f'{group}-{index}'
                directory = self.q / 'episodes' / slug
                directory.mkdir(parents=True)
                for name in ('source.mp4', 'output.mp4', 'manifest.json', 'prompt.txt'):
                    (directory / name).write_text(name)
                metadata = self.q / 'metadata' / f'{slug}.json'
                metadata.parent.mkdir(exist_ok=True)
                self.write(metadata, {'snippet': {'title': slug}, 'status': {'privacyStatus': 'public'}})
                rows.append({'slug': slug, 'title': slug, 'author': 'sobaya',
                             'source': f'batch/episodes/{slug}/source.mp4',
                             'output': f'batch/episodes/{slug}/output.mp4',
                             'manifest': f'batch/episodes/{slug}/manifest.json',
                             'metadata': f'batch/metadata/{slug}.json',
                             'sourceYoutubeId': f'original-{slug}'})
                audits.append({'slug': slug, 'passed': True, 'sha256': m.sha(directory / 'output.mp4'),
                               'manifestSha256': m.sha(directory / 'manifest.json'),
                               'duration': 30.16, 'width': 720, 'height': 1280})
            self.write(self.q / f'group-{group}.json', rows)
            for kind in ('technical', 'visual'):
                self.write(self.q / f'{kind}-audit-group-{group}.json', {'videos': audits})
        for name, data in [('queue.json', []), ('technical-audit.json', {'videos': []}),
                           ('visual-audit.json', {'videos': []})]:
            self.write(self.q / name, data)
        config = self.root / 'tools/shorts-nightly/config.json'
        config.parent.mkdir(parents=True)
        self.write(config, {'queue': 'batch', 'queues': ['batch']})

    def write(self, path, data):
        path.write_text(json.dumps(data))

    def test_complete_schema_and_publication_preserved(self):
        self.write(self.q / 'queue.json', [{'slug': 'a-0', 'status': 'published', 'youtubeId': 'posted-id'}])
        queue, technical, visual = m.prepare()
        self.assertEqual(len(queue), 34)
        self.assertEqual([row['order'] for row in queue], list(range(1, 35)))
        self.assertEqual(queue[0]['metadata'], 'metadata/a-0.json')
        self.assertEqual(queue[0]['originalYoutubeId'], 'original-a-0')
        self.assertEqual(queue[0]['youtubeId'], 'posted-id')
        self.assertEqual(queue[0]['status'], 'published')
        self.assertEqual(queue[1]['status'], 'ready')
        self.assertEqual(queue[1]['creator'], 'sobaya')
        self.assertEqual(queue[1]['eligibility']['sourceDurationSeconds'], 30.16)
        self.assertTrue(technical['allPassed'] and visual['allPassed'])

    def test_incomplete_batch_never_writes(self):
        before = {name: (self.q / name).read_bytes() for name in
                  ('queue.json', 'technical-audit.json', 'visual-audit.json')}
        (self.q / 'visual-audit-group-root.json').unlink()
        with patch('sys.argv', ['integrate_queue.py', '--write']), self.assertRaises(FileNotFoundError):
            m.main()
        self.assertEqual(before, {name: (self.q / name).read_bytes() for name in before})

    def test_changed_render_rejected(self):
        (self.q / 'episodes/b-3/output.mp4').write_text('new render')
        with self.assertRaisesRegex(ValueError, 'Changed output'):
            m.prepare()

    def test_unapproved_source_and_empty_prompt_rejected(self):
        with patch.object(m, 'source_duration', return_value=101.1):
            with self.assertRaisesRegex(ValueError, 'exceeds 101'):
                m.prepare()
        (self.q / 'episodes/a-0/prompt.txt').write_text(' ')
        with self.assertRaisesRegex(ValueError, 'Empty Studio prompt'):
            m.prepare()

    def test_private_metadata_rejected(self):
        self.write(self.q / 'metadata/a-0.json', {'snippet': {'title': 'a-0'},
                                                'status': {'privacyStatus': 'private'}})
        with self.assertRaisesRegex(ValueError, 'public unscheduled'):
            m.prepare()

    def test_write_complete_batch(self):
        with patch('sys.argv', ['integrate_queue.py', '--write']), contextlib.redirect_stdout(io.StringIO()):
            m.main()
        for name in ('queue', 'technical-audit', 'visual-audit'):
            result = m.read(self.q / f'{name}.json')
            self.assertEqual(len(result if name == 'queue' else result['videos']), 34)


if __name__ == '__main__':
    unittest.main()
