"""Concatenate the same first three complete turns from the four audition movies."""
from pathlib import Path
import json
import subprocess

P = Path(__file__).resolve().parent
KEYS = ['current', 'aoyama', 'kurono', 'shirakami']


def run(command):
    return subprocess.check_output(command, text=True)


def main():
    out = P/'out/voice-candidates/comparison'
    out.mkdir(parents=True, exist_ok=True)
    segments = []
    cursor = 0
    inputs = []
    filters = []
    for i,key in enumerate(KEYS):
        props = json.loads((P/'out/voice-candidates'/key/'props.json').read_text())
        rows = props['manifest']['dialogue']
        final = next(row for row in rows if row['id']=='intro-03')
        end = final['startFrame'] + final['durationInFrames'] + 9
        # Stop before the LINE notification begins; preserve all speech and 0.3 s pause.
        assert end < next(row['startFrame'] for row in rows if row['id']=='intro-04')-12
        video = P.parent/f'preview_voice_{key}.mp4'
        assert video.exists()
        inputs += ['-i',str(video)]
        filters += [f'[{i}:v]trim=start_frame=0:end_frame={end},setpts=PTS-STARTPTS[v{i}]',
                    f'[{i}:a]atrim=start_sample=0:end_sample={end*1600},asetpts=PTS-STARTPTS[a{i}]']
        segments.append({'candidate':key,'label':props['candidateLabel'],
            'source':str(video),'sourceStartFrame':0,'sourceEndFrameExclusive':end,
            'startFrame':cursor,'durationInFrames':end,'utterances':['intro-01','intro-02','intro-03']})
        cursor += end
    filters += [''.join(f'[v{i}][a{i}]' for i in range(len(KEYS)))+f'concat=n={len(KEYS)}:v=1:a=1[v][a]']
    target=P.parent/'preview_voice_comparison.mp4'
    run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(filters),
         '-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','medium',
         '-c:a','aac','-b:a','192k','-movflags','+faststart',str(target)])
    run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'])
    probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)]))
    video=next(stream for stream in probe['streams'] if stream['codec_type']=='video')
    audio=[stream for stream in probe['streams'] if stream['codec_type']=='audio']
    assert int(video['nb_read_frames'])==cursor
    assert (video['width'],video['height'],video['avg_frame_rate'])==(1280,720,'30/1')
    assert len(audio)==1 and audio[0]['sample_rate']=='48000'
    (out/'record.json').write_text(json.dumps({'output':str(target),'segments':segments,
        'durationInFrames':cursor,'durationSeconds':cursor/30,'fps':30,
        'fullDecodePassed':True,'subjectiveListening':False,'probe':probe},ensure_ascii=False,indent=2)+'\n')
    print(f'COMPLETE {cursor/30:.3f}s {target}')


if __name__=='__main__':
    main()
