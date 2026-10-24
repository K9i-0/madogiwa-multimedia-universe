"""Offline editing only. Never calls an image, video or speech generation service."""
from pathlib import Path
import json
import subprocess
import shutil

P = Path(__file__).resolve().parent
PUBLIC = P / 'remotion/public'
OUT = P / 'remotion/out'
M = json.loads((P / 'remotion/src/edit-manifest.json').read_text())['final']


def ff(args):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *map(str, args)], check=True)


def atempo(rate):
    filters = []
    while rate > 2:
        filters.append('atempo=2')
        rate /= 2
    filters.append(f'atempo={rate:.9f}')
    return ','.join(filters)


def cut(source, start, end, frames, target, audio=True, audio_end=None):
    rate = (end-start)/frames
    vf = f'trim=start_frame={start}:end_frame={end},setpts=(PTS-STARTPTS)/{rate:.9f},fps=30'
    args = ['-i', source, '-vf', vf, '-frames:v', frames,
            '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p']
    if audio:
        args += ['-af', f'atrim=start={start/30}:end={(audio_end or end)/30},asetpts=PTS-STARTPTS,{atempo(rate)},aresample=48000',
                 '-c:a', 'aac', '-b:a', '192k']
    else:
        args += ['-an']
    ff([*args, '-t', frames/30, '-movflags', '+faststart', target])


OUT.mkdir(exist_ok=True)
for key, edit in M['sourceEdits'].items():
    cut(P/edit['file'], edit['start'], edit['end'], edit['frames'], PUBLIC/f'edit_{key}.mp4', edit['audio'])

# Every source frame remains in chronological order; compress pauses without jump cuts.
parts = []
for i, edit in enumerate(M['theftSourceEdits']):
    target = OUT/f'theft_{i}.mp4'
    cut(P/'wan3_theft_480p.mp4', edit['start'], edit['end'], edit['frames'], target, audio_end=edit.get('audioEnd'))
    parts.append(target)
# Decode/concat avoids AAC packet padding accumulating at every speed boundary.
inputs = [item for part in parts for item in ['-i', part]]
filters = []
for i, edit in enumerate(M['theftSourceEdits']):
    filters += [f'[{i}:v]setpts=PTS-STARTPTS[v{i}]',
                f'[{i}:a]atrim=duration={edit["frames"]/30},asetpts=PTS-STARTPTS,apad=whole_dur={edit["frames"]/30}[a{i}]']
filters += [''.join(f'[v{i}][a{i}]' for i in range(len(parts)))+f'concat=n={len(parts)}:v=1:a=1[v][a]']
ff([*inputs, '-filter_complex', ';'.join(filters), '-map', '[v]', '-map', '[a]',
    '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-c:a', 'aac', '-b:a', '192k',
    '-frames:v', sum(x['frames'] for x in M['theftSourceEdits']),
    '-movflags', '+faststart', PUBLIC/'edit_theft.mp4'])

# Closed-mouth studio still from the existing 2.4-second intro, never from the harbour cut.
ff(['-ss', '2.3', '-i', PUBLIC/'anchor_intro.mp4', '-frames:v', '1', PUBLIC/'anchor_return.png'])

if 'feedback' in M:
    ff(['-ss','2','-i',PUBLIC/'anchor_intro.mp4','-t',M['feedback']['studioCueFrames']/30,
        '-an','-c:v','libx264','-crf','16',PUBLIC/'anchor_bridge.mp4'])
    shutil.copy2(P/'wan3_expert_listening_480p.mp4',PUBLIC/'expert_listening.mp4')
    for name in ['voice_anchor_to_expert.wav','voice_anchor_to_field.wav','voice_comparison_matched.wav','voice_sobaya_poison.wav']:
        shutil.copy2(P/name,PUBLIC/name)
    if 'beerExplanation' in M:
        for name in ['voice_anchor_question.wav','voice_expert_beer.wav','voice_anchor_comparison_reply.wav']:
            shutil.copy2(P/name,PUBLIC/name)

# Short environmental bed from an existing speech-free field recording.
ff(['-ss', '0', '-t', '2.2', '-i', P/'wan3_harvest_480p.mp4', '-vn',
    '-af', 'afade=t=in:d=0.08,afade=t=out:st=2.1:d=0.1', '-ar', '48000',
    '-c:a', 'pcm_s16le', PUBLIC/'field_ambience.wav'])
print('Prepared existing-media edits; no generation requests.')

# Preserve the off-camera reaction at its original pitch and speed after the fall.
if 'reaction' in M:
    reaction = M['reaction']
    ff(['-i', P/'wan3_theft_480p.mp4', '-vn', '-af',
        f'atrim=start={reaction["sourceStart"]/30}:end={reaction["sourceEnd"]/30},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st=0.76:d=0.04',
        '-ar', '48000', '-c:a', 'pcm_s16le', PUBLIC/'reaction_yotan.wav'])

if "coherentExpert" in M:
    for name in ["voice_anchor_expert_intro.wav", "voice_expert_beer_continuation.wav"]:
        shutil.copy2(P/name,PUBLIC/name)

if "smoothCuts" in M:
    shutil.copy2(P/"wan3_expert_480p.mp4",PUBLIC/M["smoothCuts"]["expertInsetSource"])
