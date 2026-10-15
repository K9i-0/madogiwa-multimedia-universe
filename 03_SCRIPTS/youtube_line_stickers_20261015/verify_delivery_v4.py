"""Verify the adopted B voice across the complete movie, preserving the v3 script."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import wave

from verify_delivery import run, timecode

P = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--video',default='final_remotion_line_stickers_v4.mp4')
    parser.add_argument('--preflight',action='store_true')
    args=parser.parse_args()
    video=P/args.video
    manifest=json.loads((P/'remotion/src/edit-manifest.json').read_text())
    script=json.loads((P/'remotion/dialogue.json').read_text())
    reference=json.loads((P/'v4_voice_replacement_reference.json').read_text())
    adopted=json.loads((P/'adopted_audio.json').read_text())['audio']
    mix=json.loads((P/'mix_record.json').read_text())
    rows=manifest['dialogue']; by_id={row['id']:row for row in rows}
    originals=reference['dialogue']; original_by_id={row['id']:row for row in originals}
    comp=manifest['composition']; fps=comp['fps']
    assert (comp['width'],comp['height'],fps)==(1280,720,30)
    assert len(rows)==len(by_id)==len(script)==len(adopted)==89
    assert [row['id'] for row in rows]==[row['id'] for row in originals]
    fields=['id','who','text','view','chapter']
    assert [[row[k] for k in fields] for row in rows]==[[row[k] for k in fields] for row in originals]
    assert [[row[k] for k in fields] for row in rows]==[[row[k] for k in fields] for row in script]
    assert {row['chapter'] for row in rows}==set(range(10))
    yametaro=[row for row in rows if row['who']=='yametaro']
    takosan=[row for row in rows if row['who']=='takosan']
    assert len(yametaro)==43 and len(takosan)==46
    for row in takosan:
        assert row['audioSha256']==original_by_id[row['id']]['audioSha256'],('Takosan changed',row['id'])
    for row in yametaro:
        settings=row['voiceSettings']; query=settings['query']
        assert '玄野武宏' in settings['model']
        assert settings['speakerId']==11 and settings['style']=='ノーマル'
        for key,value in reference['expectedSettings'].items():
            actual=settings[key] if key=='speakerId' else query[key]
            assert actual==value,(row['id'],key,actual,value)
        if row['id'] in reference['selectedIntroAudioHashes']:
            assert row['audioSha256']==reference['selectedIntroAudioHashes'][row['id']],('Adopted B opening changed',row['id'])
    assert len(reference['selectedIntroAudioHashes'])==10
    expected_files={audio['file'] for audio in adopted}
    assert {file.name for file in P.glob('voice_*.wav')}==expected_files
    for audio in adopted:
        row=by_id[audio['id']]
        assert digest(P/audio['file'])==audio['sha256']==row['audioSha256']
        public=P/'remotion/public'/row['audio']
        assert digest(public)==row['audioSha256']
        with wave.open(str(public),'rb') as wav:
            assert wav.getframerate()==48000 and wav.getnchannels()==1
            assert math.ceil(wav.getnframes()/wav.getframerate()*fps)==row['durationInFrames']
    assert digest(P/'remotion/public'/manifest['audioSrc'])==mix['mixedSha256']
    assert mix['frames']==comp['durationInFrames'] and mix['sampleRate']==48000
    with wave.open(str(P/'remotion/public'/manifest['audioSrc']),'rb') as wav:
        assert wav.getnchannels()==2 and wav.getframerate()==48000
        assert wav.getnframes()==comp['durationInFrames']*1600
    events={event['name']:event for event in mix['soundEvents']}
    assert events['original two-tone notification']['startFrame']==by_id['intro-04']['startFrame']-12
    intro_last=by_id['intro-13']
    title_frame=intro_last['startFrame']+intro_last['durationInFrames']+24
    assert events['original soft major triad title cue']['startFrame']==title_frame
    assert manifest['mainStartFrame']==by_id['main-01']['startFrame']
    assert by_id['main-01']['startFrame']>=title_frame+60
    srt=[];previous_end=0
    for row in rows:
        assert row['startFrame']-previous_end==original_by_id[row['id']]['gapBeforeFrames'],('Gap changed',row['id'])
        previous_end=row['startFrame']+row['durationInFrames']
        assert previous_end<=comp['durationInFrames']
        assert len(row['envelope'])==row['durationInFrames'] and all(math.isfinite(value) for value in row['envelope'])
        pages=row['captionSegments']
        assert ''.join(page['text'].replace('\n','') for page in pages)==row['text']
        assert [page['text'] for page in pages]==original_by_id[row['id']]['captionTextPages']
        assert pages[0]['startFrame']==0 and pages[-1]['endFrame']==row['durationInFrames']
        for i,page in enumerate(pages):
            assert len(page['text'].splitlines())<=2
            assert 0<=page['startFrame']<page['endFrame']<=row['durationInFrames']
            if i: assert pages[i-1]['endFrame']==page['startFrame']
            start=row['startFrame']+page['startFrame']; end=row['startFrame']+page['endFrame']
            srt.append(f'{len(srt)+1}\n{timecode(start,fps)} --> {timecode(end,fps)}\n{page["text"]}\n')
    (P/'subtitles_ja.srt').write_text('\n'.join(srt))
    basic={'utterances':len(rows),'subtitlePages':len(srt),'durationInFrames':comp['durationInFrames'],
        'durationSeconds':comp['durationInFrames']/fps,'scriptAndViewsPreserved':True,
        'takosanUnchangedAudio':46,'yametaroSelectedVoice':43,'openingSelectedBHashesMatched':10,
        'dialogueGapsPreserved':True,'captionTextPagesPreserved':True,
        'adoptedAudioHashes':'passed','mixedSha256':mix['mixedSha256'],
        'subjectiveListening':False}
    audit=P/'remotion/out/final-audit-v4'; audit.mkdir(parents=True,exist_ok=True)
    (audit/'preflight.json').write_text(json.dumps(basic,ensure_ascii=False,indent=2)+'\n')
    if args.preflight:
        print(json.dumps(basic,ensure_ascii=False)); return

    probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
    videos=[stream for stream in probe['streams'] if stream['codec_type']=='video']
    audios=[stream for stream in probe['streams'] if stream['codec_type']=='audio']
    assert len(videos)==len(audios)==1
    stream=videos[0]; audio=audios[0]
    assert (stream['width'],stream['height'],stream['r_frame_rate'])==(1280,720,'30/1')
    assert int(stream['nb_read_frames'])==comp['durationInFrames']
    assert audio['sample_rate']=='48000' and audio['channels']==2
    run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'])
    samples={}
    for id in ['intro-01','intro-03','intro-04','intro-07','intro-08','intro-09','intro-10','main-01','main-03','ideas-07','options-04','options-08','redraw-05','pets-04','acting-05','acting-13','inspect-03','tools-06','close-05','close-06']:
        row=by_id[id]; samples[id]=row['startFrame']+min(35,row['durationInFrames']//2)
    for id in ['options-04','pets-04','tools-02','tools-06','tools-07']:
        row=by_id[id]
        for i,page in enumerate(row['captionSegments'][1:],start=2):
            samples[f'{id}-page-{i}']=row['startFrame']+(page['startFrame']+page['endFrame'])//2
    views=set()
    for row in rows[16:]:
        if row['view'] not in views:
            samples[f'view-{row["view"]}']=row['startFrame']+row['durationInFrames']//2
            views.add(row['view'])
        if row['view'].endswith('-prompt'):
            samples[f'prompt-hold-{row["id"]}']=row['startFrame']+row['durationInFrames']+30
    samples['title']=title_frame+16; samples['final']=comp['durationInFrames']-1
    for name,frame in samples.items():
        run(['ffmpeg','-v','error','-y','-ss',str(frame/fps),'-i',str(video),'-frames:v','1',str(audit/f'{name}.png')])
    start=by_id['ideas-01']['startFrame']; end=by_id['redraw-01']['startFrame']
    excerpt=P/'preview_tips_v4.mp4'
    run(['ffmpeg','-v','error','-y','-ss',str(start/fps),'-i',str(video),'-t',str((end-start)/fps),
        '-map','0:v:0','-map','0:a:0','-c:v','libx264','-crf','18','-preset','fast',
        '-c:a','aac','-b:a','192k','-movflags','+faststart',str(excerpt)])
    report={**basic,'video':video.name,'sha256':digest(video),'bytes':video.stat().st_size,
        'resolution':[stream['width'],stream['height']],'fps':fps,
        'audio':{'codec':audio['codec_name'],'sampleRate':int(audio['sample_rate']),'channels':audio['channels']},
        'fullDecode':'passed','dialogueAndCaptionIntegrity':'passed',
        'voiceReplacementReference':'v4_voice_replacement_reference.json',
        'voiceSelection':'B / VOICEVOX:玄野武宏（ノーマル） / speaker 11 / speed 1.15',
        'techniqueExcerpt':{'file':excerpt.name,'startFrame':start,'endFrame':end,'durationSeconds':(end-start)/fps},
        'reviewFrames':[{'id':key,'frame':value,'path':f'remotion/out/final-audit-v4/{key}.png'} for key,value in samples.items()],
        'note':'Automated checks and extracted frames are separate from subjective listening/continuous visual review.'}
    (P/'delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['video','durationSeconds','bytes','utterances','subtitlePages','fullDecode']},ensure_ascii=False))


if __name__=='__main__':
    main()
