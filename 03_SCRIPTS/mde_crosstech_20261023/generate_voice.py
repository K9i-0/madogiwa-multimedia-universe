import json, subprocess, hashlib, os
from pathlib import Path

EP = Path(__file__).resolve().parent
ROOT = EP.parents[1]
CACHE = ROOT / '.local/mde-crosstech'
CACHE.mkdir(parents=True, exist_ok=True)
lines = json.loads((EP/'dialogue.json').read_text())
record_path = EP/'voice_generation_record.json'
existing = {r['id']:r for r in json.loads(record_path.read_text())} if record_path.exists() else {}
records = []
for line in lines:
    speaker = line['speaker']
    ref = ROOT/'02_CHARACTERS'/('Sobaya_voice.wav' if speaker == 'sobaya' else 'YumeTeleAnchor_voice.wav')
    seed = 42 if speaker == 'sobaya' else 2026
    caption = '落ち着いた経営者インタビュー。自信を持って自然に話す。' if speaker == 'sobaya' else '落ち着いた地方局ニュース読み。標準語で、明瞭かつ均一な速度、抑制された抑揚で真面目に話す。'
    raw = CACHE/f"{line['id']}_{speaker}_raw.wav"
    out = EP/f"{line['id']}_{speaker}.wav"
    log = CACHE/f"{line['id']}.log"
    cached = existing.get(line['id'])
    if out.exists() and cached and hashlib.sha256(out.read_bytes()).hexdigest() == cached['sha256']:
        records.append(cached)  # Preserve the actual original TTS input for homophonic display edits.
        print('REUSING', line['id'], cached['duration'], flush=True)
        continue
    if not out.exists():
        print('GENERATING', line['id'], line['text'], flush=True)
        with log.open('w') as f:
            subprocess.run([str(ROOT/'tools/irodori_speak.sh'), line['spoken'], str(raw), str(ref), str(seed), caption], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, check=True)
        processed = CACHE/f"{line['id']}_processed.wav"
        if speaker == 'sobaya':
            subprocess.run([str(ROOT/'tools/sobaya_monsterize.sh'),str(raw),str(processed)],check=True)
        else:
            processed = raw
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(processed),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','48000','-ac','1',str(out)],check=True)
    seconds = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)]))
    record = dict(line, path=out.name, duration=seconds, model='Aratako/Irodori-TTS-v4-Large' if speaker=='sobaya' else 'Aratako/Irodori-TTS-v4.1-Small', reference=str(ref.relative_to(ROOT)), reference_sha256=hashlib.sha256(ref.read_bytes()).hexdigest(), seed=seed, caption=caption, duration_scale=1.0, cfg_text=3, trim=True, monsterize=speaker=='sobaya', sha256=hashlib.sha256(out.read_bytes()).hexdigest())
    records.append(record)
    (EP/'voice_generation_record.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    print('DONE',line['id'],seconds,flush=True)

record_path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
