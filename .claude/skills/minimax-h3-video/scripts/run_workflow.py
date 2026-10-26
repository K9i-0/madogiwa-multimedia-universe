#!/usr/bin/env python3
"""Submit once, persist prompt_id, resume polling, and validate the downloaded MP4."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
import urllib.parse
import uuid


def api(server, path, payload=None):
    req = urllib.request.Request(server.rstrip('/') + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def save(path, data):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('workflow', type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--server', default='http://127.0.0.1:8188')
    p.add_argument('--timeout', type=int, default=7200)
    p.add_argument('--poll', type=float, default=15)
    a = p.parse_args()
    if a.timeout <= 0 or a.poll <= 0:
        p.error('timeout/poll must be positive')
    if not shutil.which('ffprobe'):
        p.error('ffprobe is required before submission')
    graph = json.loads(a.workflow.read_text())
    digest = hashlib.sha256(a.workflow.read_bytes()).hexdigest()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    state_path = a.out.with_suffix('.job.json')
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if state['workflow_sha256'] != digest or state['server'] != a.server:
            p.error('Existing job belongs to different inputs/server; choose a new output path')
        if state.get('status') == 'verified' and a.out.exists():
            print('Already verified:', a.out)
            return
        if state.get('status') == 'submission_unknown':
            p.error('Submission response was lost. Inspect server queue/history; do not blindly resubmit.')
    else:
        if a.out.exists():
            p.error('Output already exists without job state; choose a new output path')
        api(a.server, '/system_stats')
        state = dict(server=a.server, workflow_sha256=digest, client_id=uuid.uuid4().hex,
                     started_unix=time.time(), status='submission_unknown')
        save(state_path, state)  # Do not retry a POST after a lost response.
        result = api(a.server, '/prompt', {'prompt': graph, 'client_id': state['client_id']})
        if result.get('error') or not result.get('prompt_id'):
            state.update(status='rejected', response=result)
            save(state_path, state)
            raise RuntimeError(result)
        state.update(prompt_id=result['prompt_id'], status='queued')
        save(state_path, state)
    if not state.get('prompt_id'):
        p.error('No submitted prompt_id. Correct inputs and use a new output path.')
    print('prompt_id:', state['prompt_id'], flush=True)
    deadline = time.monotonic() + a.timeout
    while time.monotonic() < deadline:
        entry = api(a.server, '/history/' + state['prompt_id']).get(state['prompt_id'])
        if entry:
            status = entry.get('status', {})
            if status.get('status_str') == 'error':
                state.update(status='failed', messages=status.get('messages'))
                save(state_path, state)
                raise RuntimeError(state['messages'])
            if status.get('completed'):
                break
        print('Waiting; elapsed seconds:', round(time.time() - state['started_unix']), flush=True)
        time.sleep(a.poll)
    else:
        raise TimeoutError('Polling stopped; server job may still run. Resume this same command; do not resubmit.')
    videos = [f for output in entry.get('outputs', {}).values()
              for key in ('videos', 'gifs', 'images') for f in output.get(key, [])
              if f.get('filename', '').lower().endswith('.mp4')]
    if len(videos) != 1:
        raise RuntimeError(f'Expected one MP4, received {len(videos)}')
    item = videos[0]
    query = urllib.parse.urlencode({k: item.get(k, 'output' if k == 'type' else '')
                                   for k in ('filename', 'subfolder', 'type')})
    part = a.out.with_suffix('.part.mp4')
    with urllib.request.urlopen(a.server.rstrip('/') + '/view?' + query, timeout=600) as r, part.open('wb') as f:
        shutil.copyfileobj(r, f)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames',
        '-show_streams', '-show_format', '-of', 'json', str(part)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    cond = next(n['inputs'] for n in graph.values() if n['class_type'] in
                ('MiniMaxH3ImageToVideo', 'MiniMaxH3ReferenceToVideo'))
    if (v['width'], v['height']) != (cond['width'], cond['height']):
        raise RuntimeError('Output resolution mismatch')
    if int(v['nb_read_frames']) != cond['length'] or v['avg_frame_rate'] != '24/1':
        raise RuntimeError('Output frame count/fps mismatch')
    if not any(s['codec_type'] == 'audio' for s in probe['streams']):
        raise RuntimeError('Native audio stream missing')
    part.replace(a.out)
    state.update(status='verified', elapsed_seconds=round(time.time() - state['started_unix'], 2),
                 output_sha256=hashlib.sha256(a.out.read_bytes()).hexdigest(), probe=probe)
    save(state_path, state)
    print('MP4 structure verified (visual/audio review still required):', a.out)


if __name__ == '__main__':
    main()
