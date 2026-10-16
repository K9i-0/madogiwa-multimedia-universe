#!/usr/bin/env python3
"""Validate all 34 finished Shorts, then optionally install the complete queue.

Default is read-only. --write installs the complete audited batch; it never uploads.
Incomplete groups, changed renders, missing prompts, and private/scheduled metadata
fail before any queue or aggregate audit is written.
"""
import argparse
from contextlib import ExitStack
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

Q = Path(__file__).resolve().parent
ROOT = Q.parents[1]
GROUPS = ('a', 'b', 'c', 'root')
EXPECTED = 34
POLICY = 'studio-prompt-max101s-20261016'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def repo_file(value):
    path = ROOT / value
    require(not Path(value).is_absolute() and path.resolve().is_relative_to(ROOT.resolve()),
            f'Expected repository-relative path: {value}')
    require(path.is_file(), f'Missing file: {value}')
    return path


def source_duration(path):
    result = subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(path),
    ], text=True, timeout=30)
    return float(result.strip())


def audit_map(path, slugs):
    document = read(path)
    videos = document['videos']
    indexed = {video['slug']: video for video in videos}
    require(len(indexed) == len(videos) and set(indexed) == slugs,
            f'Incomplete or unexpected audit set: {path.name}')
    require(all(video.get('passed') is True for video in videos),
            f'Failed audit: {path.name}')
    return indexed


def prepare():
    rows, technical, visual = [], {}, {}
    for group in GROUPS:
        group_rows = read(Q / f'group-{group}.json')
        require(isinstance(group_rows, list), f'Invalid group-{group}.json')
        slugs = {row['slug'] for row in group_rows}
        require(len(slugs) == len(group_rows), f'Duplicate slug in group {group}')
        require(not slugs.intersection(row['slug'] for row in rows),
                f'Duplicate slug across group {group}')
        technical.update(audit_map(Q / f'technical-audit-group-{group}.json', slugs))
        visual.update(audit_map(Q / f'visual-audit-group-{group}.json', slugs))
        rows.extend(group_rows)
    require(len(rows) == EXPECTED, f'Expected exactly {EXPECTED} videos; got {len(rows)}')
    existing_rows = read(Q / 'queue.json') if (Q / 'queue.json').exists() else []
    existing = {row['slug']: row for row in existing_rows}
    require(len(existing) == len(existing_rows), 'Existing queue has duplicate slugs')
    require(set(existing).issubset(row['slug'] for row in rows),
            'Existing queue contains rows outside this batch; refusing to remove them')
    queue, youtube_ids = [], set()
    for order, row in enumerate(rows, 1):
        slug = row['slug']
        a, v = technical[slug], visual[slug]
        output = repo_file(row['output'])
        source = repo_file(row['source'])
        manifest = repo_file(row['manifest'])
        metadata = repo_file(row['metadata'])
        require(metadata.resolve().is_relative_to(Q.resolve()), f'Metadata outside batch: {slug}')
        m = read(metadata)
        require(m.get('status', {}).get('privacyStatus') == 'public'
                and not m['status'].get('publishAt'), f'Expected public unscheduled metadata: {slug}')
        require(bool(m.get('snippet', {}).get('title', '').strip()), f'Missing upload title: {slug}')
        require(sha(output) == a['sha256'] == v['sha256'], f'Changed output or stale visual audit: {slug}')
        require(sha(manifest) == a['manifestSha256'], f'Changed manifest: {slug}')
        if v.get('manifestSha256'):
            require(v['manifestSha256'] == a['manifestSha256'], f'Stale visual manifest: {slug}')
        if a.get('sourceSha256'):
            require(sha(source) == a['sourceSha256'], f'Changed original source: {slug}')
        require(0 < a['duration'] <= 101 and (a['width'], a['height']) == (720, 1280),
                f'Output exceeds the approved size/duration: {slug}')
        duration = source_duration(source)
        require(0 < duration <= 101, f'Original source exceeds 101 seconds: {slug}')
        prompt_value = row.get('eligibility', {}).get('promptPath',
                        str(manifest.with_name('prompt.txt').relative_to(ROOT)))
        prompt = repo_file(prompt_value)
        require(bool(prompt.read_text().strip()), f'Empty Studio prompt: {slug}')
        author = row.get('creator', row.get('author'))
        require(author in ('k9i', 'sobaya'), f'Missing or unknown author: {slug}')
        require(not row.get('author') or row['author'] == author, f'Conflicting author: {slug}')
        original_id = row.get('sourceYoutubeId', row.get('originalYoutubeId'))
        require(original_id and original_id not in youtube_ids, f'Missing/duplicate original YouTube ID: {slug}')
        youtube_ids.add(original_id)
        result = {
            **existing.get(slug, {}),
            'order': order, 'batch': 'studio-20261016', 'slug': slug,
            'title': row['title'], 'creator': author,
            'source': row['source'], 'originalYoutubeId': original_id,
            'manifest': row['manifest'], 'output': row['output'],
            'status': 'ready', 'metadata': str(metadata.relative_to(Q)),
            'eligibility': {'policy': POLICY, 'sourceDurationSeconds': duration,
                            'promptPath': str(prompt.relative_to(ROOT))},
        }
        for key in ('episodeId', 'generationId'):
            if row.get(key):
                result[key] = row[key]
        # Re-running integration must not erase a publication or resume record.
        old = existing.get(slug, {})
        if old.get('youtubeId') or old.get('status') == 'published':
            result['status'] = 'published'
        queue.append(result)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    common = {'checkedAt': now, 'allPassed': True, 'fullPlaybackListening': False,
              'scope': 'All 34 finished Shorts; grouped audits merged and current file hashes verified'}
    return queue, {**common, 'videos': [technical[r['slug']] for r in queue]}, {
        **common, 'videos': [visual[r['slug']] for r in queue]}


def atomic_write(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Install the entire complete batch, never upload')
    args = parser.parse_args()
    with ExitStack() as stack:
        if args.write:
            # Same global and queue locks as tools/shorts-nightly/run.py.
            config = read(ROOT / 'tools/shorts-nightly/config.json')
            state = ROOT / '.local/shorts-nightly'
            state.mkdir(parents=True, exist_ok=True)
            paths = [state / 'upload.lock']
            for folder in sorted({ROOT / item for item in config.get('queues', [config['queue']])} | {Q}):
                (folder / 'youtube_uploads').mkdir(exist_ok=True)
                paths.append(folder / 'youtube_uploads/.lock')
            for path in paths:
                handle = stack.enter_context(path.open('a'))
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        queue, technical, visual = prepare()
        if args.write:
            atomic_write(Q / 'technical-audit.json', technical)
            atomic_write(Q / 'visual-audit.json', visual)
            atomic_write(Q / 'queue.json', queue)
        print(json.dumps({'action': 'integrated' if args.write else 'validated',
                          'total': len(queue), 'creators': {
                              creator: sum(row['creator'] == creator for row in queue)
                              for creator in ('k9i', 'sobaya')},
                          'uploaded': False}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, FileNotFoundError, BlockingIOError) as exc:
        raise SystemExit(f'Queue unchanged: {exc}')
