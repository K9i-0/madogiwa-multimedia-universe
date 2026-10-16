"""Screen the two v7 Takosan revisions; reuse the v6 ASR/VAD setup and flags."""
import difflib
import hashlib
import json
import subprocess

from audit_voice_v6 import P, R, norm, review_signals, processor, model, vad, get_speech_timestamps
from audit_voice_v6 import np, sf, torch, write_json

BASELINE = '0a3e1f3f'
CHANGED = {'tips-01', 'settings-03'}
MORA_TERMS = {
    'tips-01': ['ダイニダン', 'ハンバイニムケテジュンビチュウ'],
    'settings-03': ['ウルトラ', 'フクスウノエエジェント', 'ブンタン', 'ヘエレツ'],
}


def screen(row, source):
    x, sr = sf.read(source)
    assert x.ndim == 1 and sr == 48000 and len(x) and np.isfinite(x).all()
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-f','f32le','-ac','1','-ar','16000','-'])
    audio = np.frombuffer(raw,dtype='<f4').copy()
    inputs = processor(audio,sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
    with torch.inference_mode():
        generated = model.generate(**inputs,language='ja',task='transcribe',max_new_tokens=220)
    recognized = processor.batch_decode(generated,skip_special_tokens=True)[0]
    speech = {str(level):get_speech_timestamps(torch.from_numpy(audio),vad,sampling_rate=16000,
        threshold=level,min_speech_duration_ms=80,min_silence_duration_ms=100,speech_pad_ms=0,return_seconds=True)
        for level in [.25,.5]}
    rms = np.array([np.sqrt(np.mean(audio[i:i+160]**2)) for i in range(0,len(audio),160)])
    last = speech['0.5'][-1]['end'] if speech['0.5'] else 0
    tail = rms[min(len(rms),round(last*100)):]
    full_scale = (x <= -1) | (x >= 32767/32768)
    edges = np.diff(np.pad(full_scale.astype(int),(1,1)))
    starts,ends = np.flatnonzero(edges==1),np.flatnonzero(edges==-1)
    query = row['voiceSettings']['query']
    mora = ''.join(m['text'] for phrase in query['accent_phrases'] for m in phrase['moras'])
    assert all(term in mora for term in MORA_TERMS[row['id']]), (row['id'],mora)
    item = {'id':row['id'],'who':row['who'],'audioSha256':row['audioSha256'],'audio':row['audio'],
        'expected':row['text'],'spoken':row['spoken'],'recognized':recognized,
        'similarity':round(difflib.SequenceMatcher(None,norm(row['spoken']),norm(recognized)).ratio(),3),
        'durationSeconds':len(x)/sr,'sampleRate':sr,'peak':float(np.max(np.abs(x))),
        'nonFiniteSamples':int(np.sum(~np.isfinite(x))),'clippedSamples':int(np.sum(np.abs(x)>=.999)),
        'sileroVAD':speech,'tailAfterVadSeconds':round(len(audio)/16000-last,3),
        'tailAfterVadPeakRmsDb':round(float(20*np.log10(max(float(tail.max()),1e-9))),2) if len(tail) else None,
        'actualPcmFullScaleSamples':int(full_scale.sum()),
        'maxPcmFullScaleRunSamples':int(max(ends-starts)) if len(starts) else 0,
        'voiceSettings':row['voiceSettings'],'postprocessingApplied':bool(row.get('audioProcessing')),
        'voicevoxMoraEvidence':{'moraSequence':mora,'kana':query['kana'],
            'expectedTerms':MORA_TERMS[row['id']],'allTermsPresent':True}}
    item.update(review_signals(item))
    return item


def main():
    current = json.loads((P.parent/'voice_record.json').read_text())['lines']
    baseline = {r['id']:r for r in json.loads(subprocess.check_output(['git','show',
        f'{BASELINE}:03_SCRIPTS/youtube_line_stickers_20261015/voice_record.json'],cwd=R,text=True))['lines']}
    adopted = {r['id']:r for r in json.loads((P.parent/'adopted_audio.json').read_text())['audio']}
    changed = {r['id'] for r in current if any(r.get(k)!=baseline[r['id']].get(k)
        for k in ['who','text','reading','voiceSettings','audioSha256'])}
    assert changed == CHANGED, changed
    assert len(current)==107 and set(adopted)==set(baseline)=={r['id'] for r in current}
    result, preserved = [], []
    for row in current:
        source = P/'public'/row['audio']
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest == row['audioSha256'] == hashlib.sha256((P.parent/adopted[row['id']]['file']).read_bytes()).hexdigest()
        if row['id'] not in CHANGED:
            assert row['voiceSettings']==baseline[row['id']]['voiceSettings']
            assert digest==baseline[row['id']]['audioSha256']
            preserved.append(row['id'])
            continue
        assert row['who']=='takosan' and row['voiceSettings']['speakerId']==61
        item = screen(row,source); result.append(item)
        print(row['id'],item['recognized'],'flags:',item['machineReviewFlags'],flush=True)
    report = {'version':7,'baselineCommit':BASELINE,'status':'automated_screening','subjectiveListening':False,
        'asrModel':'openai/whisper-small','expectedTextPrompt':False,'vadModel':'Silero VAD',
        'adoptedUtterances':len(current),'changedUtteranceIds':sorted(CHANGED),'changedUtterances':result,
        'unchangedWaveformIdsVerified':preserved,'allWaveformHashesVerified':True,
        'allUnchangedSettingsAndWaveformsPreserved':len(preserved)==105,'allChangedLinesScreened':len(result)==2,
        'machineFlaggedUtteranceIds':[r['id'] for r in result if r['machineReviewFlags']],
        'note':'ASR/VAD, exact VV synthesis-mora queries and waveform hashes only. No subjective listening pass.'}
    report_path = P.parent/'voice_audit_v7.json'
    if report_path.exists():
        old = json.loads(report_path.read_text())
        if {r['audioSha256'] for r in old.get('changedUtterances',[])} == {r['audioSha256'] for r in result}:
            if old.get('screeningReview'):
                report['screeningReview'] = old['screeningReview']
    write_json(report_path,report)
    print('PASS: 107 waveforms verified; 105 v6 waveforms/settings preserved; 2 v7 voices screened.')


if __name__=='__main__':
    main()
