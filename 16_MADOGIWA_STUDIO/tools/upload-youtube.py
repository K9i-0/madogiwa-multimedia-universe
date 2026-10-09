#!/usr/bin/env python3
"""Resume a direct YouTube upload; never store video bytes or credentials in Studio.
Metadata: YouTube videos.insert {snippet, status}. Defaults to private.
After completion register the returned ID with Studio's register_youtube_video.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

PRIVATE = Path.home() / '.config/mmu-youtube'


def save_private(path, data):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
    os.replace(temp, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--record', type=Path, required=True, help='Non-secret result JSON (video ID and SHA256)')
    args = parser.parse_args()
    video = args.video.resolve()
    size = video.stat().st_size
    with video.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if args.record.exists():
        record = json.loads(args.record.read_text())
        if record.get('sha256') != digest:
            parser.error('Existing record belongs to a different file. Use a new record path.')
        print(json.dumps(record, ensure_ascii=False)); return
    metadata = json.loads(args.metadata.read_text())
    if not metadata.get('snippet', {}).get('title'):
        parser.error('metadata.snippet.title is required')
    metadata.setdefault('status', {}).setdefault('privacyStatus', 'private')
    metadata['status'].setdefault('embeddable', True)
    subprocess.run(['python3', str(Path(__file__).resolve().parents[1] / 'youtube-auth/manage.py'), 'access-token'], check=True)
    token = json.loads((PRIVATE / 'access-token.json').read_text())['access_token']

    def call(url, data, method, headers):
        request = urllib.request.Request(url, data=data, method=method, headers={
            'Authorization': 'Bearer ' + token, **headers})
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return response.status, response.headers, response.read()
        except urllib.error.HTTPError as error:
            if error.code == 308:
                return error.code, error.headers, b''
            # URLs carry resumable upload tokens: never print exception/URL/body.
            raise SystemExit(f'YouTube HTTP {error.code}. Session retained privately; rerun to resume. For 404/410 inspect the channel before explicitly removing the expired session.') from None
        except urllib.error.URLError:
            raise SystemExit('Network error. Session retained privately; rerun to resume.') from None

    session_file = PRIVATE / 'uploads' / (digest + '.json')
    if session_file.exists():
        session = json.loads(session_file.read_text())
    else:
        _, headers, _ = call('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status&notifySubscribers=false', json.dumps(metadata).encode(), 'POST', {
            'Content-Type': 'application/json; charset=UTF-8', 'X-Upload-Content-Length': str(size), 'X-Upload-Content-Type': 'video/mp4'})
        session = {'url': headers['Location'], 'sha256': digest, 'file': str(video)}
        save_private(session_file, session)
    # Query status even after a previous process lost its final response.
    status, headers, body = call(session['url'], b'', 'PUT', {'Content-Length': '0', 'Content-Range': f'bytes */{size}'})
    offset = int(headers.get('Range', 'bytes=0--1').rsplit('-', 1)[-1]) + 1 if headers.get('Range') else 0
    with video.open('rb') as stream:
        while status == 308 and offset < size:
            stream.seek(offset)
            chunk = stream.read(8 * 1024 * 1024)
            end = offset + len(chunk) - 1
            status, headers, body = call(session['url'], chunk, 'PUT', {'Content-Type': 'video/mp4', 'Content-Length': str(len(chunk)), 'Content-Range': f'bytes {offset}-{end}/{size}'})
            offset = int(headers['Range'].rsplit('-', 1)[-1]) + 1 if status == 308 and headers.get('Range') else end + 1
            print(f'Uploaded {offset}/{size} bytes', flush=True)
    if status not in (200, 201):
        raise SystemExit('Upload incomplete. Rerun to resume.')
    result = json.loads(body)
    record = {'video_id': result['id'], 'url': 'https://www.youtube.com/watch?v=' + result['id'], 'sha256': digest, 'file': video.name, 'status': result.get('status')}
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(record, ensure_ascii=False))

if __name__ == '__main__':
    main()
