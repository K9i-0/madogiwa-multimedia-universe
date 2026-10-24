"""Generate adopted normal-speed Aoyama narration with shared reading provenance."""
import concurrent.futures, hashlib, importlib.util, json, math, os, urllib.parse, urllib.request, wave
from pathlib import Path
P = Path(__file__).resolve().parent
ROOT = P.parents[2]
E = P.parent
BASE = 'http://127.0.0.1:50021'
spec = importlib.util.spec_from_file_location('readings', ROOT/'.claude/skills/voicevox-control/scripts/prepare_readings.py')
helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
dictionary = helper.load_dictionary()
def api(endpoint, params=None, body=None):
    url = BASE+'/'+endpoint
    if params: url += '?'+urllib.parse.urlencode(params)
    request = urllib.request.Request(url, data=body, headers={'Content-Type':'application/json'})
    if endpoint in ('audio_query','synthesis'): request.method='POST'
    with urllib.request.urlopen(request, timeout=180) as response: return response.read()
version = json.loads(api('version'))
speakers = json.loads(api('speakers'))
assert any(s['name']=='青山龍星' and any(t['id']==13 for t in s['styles']) for s in speakers)
rows = json.loads((P/'dialogue-source.json').read_text())
# Context-specific readings are scoped to the adopted line, never single-character replacements.
fixes = {
 'n003': [('会社の金で','会社のかねで')],
 'n012': [('六畳','ろくじょう'),('木箱が一つ','木箱がひとつ')],
 'n018': [('端に','はしに')],
 'n020': [('弾いて','はじいて')],
 'n021': [('畳の縁','たたみのへり'),('三つ','みっつ')],
 'n028': [('十センチ','じゅっセンチ')],
 'n029': [('人が','ひとが')],
 'n030': [('右頬','みぎほお')],
 'n034': [('その人が','そのひとが')],
 'n047': [('口が開きません','口があきません')],
 'n060': [('もう一本','もういっぽん')],
 'n066': [('祈祷','きとう')],
 'n072': [('壊した面を','壊しためんを')],
 'n075': [('壁の方へ','壁のほうへ')],
 'n076': [('四人で','よにんで')],
 'n077': [('割れた面を','割れためんを')],
 'n078': [('三つ','みっつ')],
 'n079': [('先生は面を','先生はめんを')],
 'n089': [('両頬','りょうほお')],
 'n100': [('顎を','あごを')],
 'n102': [('顎から','あごから')],
 'n111': [('錠前','じょうまえ')],
}
character_rows={'n045':'sobaya_return.wav','n081':'f_warning.wav','n095':'f_false_release.wav','n099':'sobaya_turn.wav'}
prepared=[]
for row in rows:
    r=helper.prepare_row(row,dictionary,scopes=['mmu','y-village'])
    if row['id'] in fixes:
        speech=r['speech']
        for a,b in fixes[row['id']]:
            assert a in speech,(row['id'],a,speech)
            speech=speech.replace(a,b)
        r=helper.prepare_row({**row,'speech_override':speech},dictionary,scopes=['mmu','y-village'])
        r['reading_report']['context_fixes']=fixes[row['id']]
    if r['id'] in character_rows:
        r['engine']='irodori';r['file']='../'+character_rows[r['id']]
        r['speaker']='sobaya' if r['id'] in ['n045','n099'] else 'f'
    prepared.append(r)
(P/'dialogue.json').write_text(json.dumps(prepared,ensure_ascii=False,indent=2)+'\n')
def generate(r):
    if r['engine']!='voicevox':return r
    query=json.loads(api('audio_query',{'text':r['speech'],'speaker':13}))
    query.update(speedScale=1.0,pitchScale=0.0,intonationScale=0.85,volumeScale=1.0,
                 prePhonemeLength=0.14,postPhonemeLength=0.22,outputSamplingRate=24000,outputStereo=False)
    fingerprint=hashlib.sha256(json.dumps({'query':query,'version':version,'style':13},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    wav=E/'voice'/f"{r['id']}_{fingerprint[:12]}.wav"
    if not wav.exists():
        data=api('synthesis',{'speaker':13},json.dumps(query).encode())
        assert data[:4]==b'RIFF';wav.write_bytes(data)
    (E/'queries'/f"{r['id']}.json").write_text(json.dumps(query,ensure_ascii=False,indent=2)+'\n')
    with wave.open(str(wav)) as w:
        assert w.getframerate()==24000 and w.getnchannels()==1
        seconds=w.getnframes()/w.getframerate()
    result={**r,'file':str(wav.relative_to(E)),'seconds':seconds,'kana':query['kana'],
            'cacheHash':fingerprint,'engineVersion':version,'styleId':13}
    print(r['id'],f'{seconds:.2f}s',query['kana'],flush=True)
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    manifest=list(pool.map(generate,prepared))
(P/'voice-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Narration seconds',sum(r.get('seconds',0) for r in manifest),flush=True)
