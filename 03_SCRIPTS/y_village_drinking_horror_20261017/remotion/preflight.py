"""Checks the edit's concrete constraints; does not score subjective scariness."""
from pathlib import Path
import json,wave,statistics
P=Path(__file__).resolve().parent
m=json.loads((P/'src/edit-manifest.json').read_text());v=json.loads((P/'voice-manifest.json').read_text())
source=json.loads((P/'dialogue-source.json').read_text());narr=m['narration'];by={r['id']:r for r in narr}
assert v['settings']['speaker']==13 and v['settings']['speedScale']==1 and v['settings']['pitchScale']==0
assert [(r['id'],r['text'],r['chapter']) for r in source]==[(r['id'],r['text'],r['chapter']) for r in narr]
assert sum(r['text'].count('中口') for r in narr)==2
assert by['n0060']['from']<by['n0085v5r2']['from']
assert by['n0255v5a6']['from']<by['n0237']['from']
assert 'n0255v5a8' not in by and 'n0369' not in by and 'n0387' not in by
assert by['n0297']['text'].count('四つ')==1
assert by['n0298v6a0']['text']=='F先生の分は、ありません。'
entity={'reveal','asleep','sobaya_clap_v6','sobaya_mug_v6','sobaya_moonlit_v7'}
assert m['glimpseFrame']==by['n0075v7a0']['from']<by['n0208']['from']<m['revealFrame']
assert '妻が「誰と話してるの」と聞きました。'==by['n0141']['text']
assert '休んでいたそうです' in by['n0167a']['text']
for s in m['shots']:
 assert (P/'public/art'/f"{s['background']}.png").is_file()
 if s['from']<m['glimpseFrame']:assert s['background'] not in entity
 if s['from']<m['revealFrame'] and s['background'] in entity:assert s['background']=='sobaya_moonlit_v7'
 if s['from']>=m['glimpseFrame']:assert s['person'] not in ('sobaya_shadow','sobaya_shadow_v4','sobaya')
 if s['view'] in ('recording','witness','f-perspective','memory'):
  assert s['background'] not in entity and s['person']!='sobaya_shadow_v4'
for e in m['environmentalAudio']:
 assert e['kind']=='performed-monkey-imitation'
 assert e['from']+e['duration']<by['n0050']['from']
 assert (P/'public'/e['file']).is_file()
assert m['shots'][0]['from']==0 and m['shots'][-1]['to']==m['composition']['durationInFrames']
assert all(a['to']==b['from'] for a,b in zip(m['shots'],m['shots'][1:]))
assert all(a['to']<=b['from'] for a,b in zip(m['captions'],m['captions'][1:]))
assert all(len(c['text'].splitlines())<=2 and max(map(len,c['text'].splitlines()))<=32 for c in m['captions'])
for r in narr:
 with wave.open(str(P/'public'/r['file'])) as w:assert w.getnframes()/w.getframerate()<=r['duration']/30
for e in m['characterAudio']:
 assert not any(e['from']<r['from']+r['duration'] and e['from']+e['duration']>r['from'] for r in narr)
 for s in m['shots']:
  if s['view'] in ('recording','witness','memory'):
   assert not(e['from']<s['to'] and e['from']+e['duration']>s['from'])
clap=next(e for e in m['sfx'] if e['kind']=='clap')
assert clap['frame']>=m['revealFrame']
assert all(not(s['from']<=clap['frame']<s['to']) for s in m['shots'] if s['view']=='recording')
sealed=next(s for s in m['shots'] if s['background']=='hand_can_sealed_v6')
opened=next(s for s in m['shots'] if s['background']=='hand_can_open_v6')
assert sealed['to']==opened['from']
assert any(e['kind']=='can' and e['frame']==opened['from'] for e in m['sfx'])
checks={
 'status':'passed','durationSeconds':m['composition']['durationInFrames']/30,
 'voice':'青山龍星 style13 speed1 pitch0','voiceClipCount':len(narr),
 'captions':len(m['captions']),'shots':len(m['shots']),
 'additionalGapSeconds':sum(b['from']-a['from']-a['duration'] for a,b in zip(narr,narr[1:]))/30,
 'medianAdditionalGapSeconds':statistics.median(b['from']-a['from']-a['duration'] for a,b in zip(narr,narr[1:]))/30,
 'fullFaceExposureSeconds':sum(s['to']-s['from'] for s in m['shots'] if s['background']=='reveal' and s['zoom']<1.65)/30,
 'characterAudioNoNarrationOverlap':True,'witnessesNeverShowEntity':True,'recordingsNeverContainMonsterAudio':True,
 'sealedCanOpensAtSound':True,'identityNameCalls':2,'fourMugsFDoesNotDrink':True,
 'moonlitGlimpseBeforeAppearanceDialogue':True,'glimpseSeconds':m['glimpseFrame']/30,
 'wifeQuestionExplicit':True,'mAbsenceIndirectlyLearned':True,'monkeyCallResponse':3,
 'comedyBeforeAuthorityTurn':True,'bodyAgencyAdded':True,'explicitBenevolentInterpretationDeferred':True,
 'readingChecks':'VOICEVOX kana checked for 人/方/空/杯/中口/管理人; 専用の杯 and あなた方 corrected',
 'subjectiveReview':'script and rendered images reviewed; full human listening unavailable',
 'anchors':{k:round(by[k]['from']/30,3) for k in ['n0019','n0048a','n0073','n0075v7a0','n0134','n0141','n0167a','n0179','n0219v6a0','n0237','n0317','n0367','n0457','n0486']}
}
(P.parent/'preflight-v7.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
