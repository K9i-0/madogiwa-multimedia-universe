"""Adopt the changed lines and build v3 from their measured durations."""
from pathlib import Path
import json, os, hashlib
P = Path(__file__).resolve().parent
rows = json.loads((P/'out/voice_progress_v3.json').read_text())
expected = json.loads((P/'dialogue-v3.json').read_text())
assert [r['id'] for r in rows] == [r['id'] for r in expected]
for generated, requested in zip(rows, expected):
    for key in ('who', 'text', 'chapter', 'view'):
        assert generated[key] == requested[key], f"Regenerate audio before adopting changed {requested['id']} {key}"
cursor = 12
for d in rows:
    if not d.get('reuseAudio'):
        src = P/'public'/d['audio']; name = f"clip_v3_{d['id']}_{d['who']}.wav"; dst = P.parent/name
        if not dst.exists(): dst.write_bytes(src.read_bytes())
        assert hashlib.sha256(dst.read_bytes()).hexdigest() == d['audioSha256']
        link = P/'public'/name
        if not link.exists(): link.symlink_to(os.path.relpath(dst, link.parent))
        d['audio'] = name
    d['startFrame'] = cursor
    cursor += d['durationInFrames'] + d.get('pause', 9)
end = cursor + 42
m = {'composition': {'width':1280,'height':720,'fps':30,'durationInFrames':end}, 'mainStartFrame':next(d['startFrame'] for d in rows if d['chapter'].startswith('2.')), 'endingStartFrame':next(d['startFrame'] for d in rows if d['chapter'].startswith('8.')), 'voiceModel':'Irodori Yametaro + VOICEVOX Chugoku Usagi', 'dialogue':rows, 'clips':[], 'creditsInDescription':True}
(P/'src/edit-manifest-v3.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
record=[]
for d in rows:
    r={k:d[k] for k in ('id','who','text','spoken','audio','audioSha256','durationInFrames','startFrame','sampleRate')}
    r['reusedFromV2']=bool(d.get('reuseAudio'))
    r['voiceSettings']={k:v for k,v in d['voiceSettings'].items() if k!='query'}
    if 'query' in d['voiceSettings']:r['savedQuerySha256']=hashlib.sha256(json.dumps(d['voiceSettings']['query'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    record.append(r)
(P.parent/'voice_record_v3.json').write_text(json.dumps({'subjectiveListening':False,'exactQueries':'remotion/src/edit-manifest-v3.json','lines':record},ensure_ascii=False,indent=2)+'\n')
new_count=sum(not d.get('reuseAudio') for d in rows)
script='''# Tripoで窓際族を3Dにする — 完成版v3

2026-10-14のフィードバックを反映。画面上の文字を厳選し、Excel風の数式バー・セル番地を撤去。公式サービスのロゴと実ページを出典付きで紹介する。API監視の詳細は削り、準備・依頼・生成物の確認を説明。ゲームはUnityを一般例として紹介し、投稿者がFlutterエンジニアなのでFlutter Sceneでも動かしている実例へつなぐ。両者の表情と聞き手の反応を台詞ごとに指定する。

登場：やめ太郎（Irodori v4.1-Small、正典参照・seed7・CFG5）、たこさん（VOICEVOX中国うさぎ・ノーマル61、速度1.1・音高0）。新規{new_count}発話、v2から{len(rows)-new_count}発話を再利用。元版は保持。

そば屋の縦832×1108のWan回転動画、四方向入力、たこさんの前後2画像、採用モデルと修正資料は実素材。冒頭のBlender版制作担当は劇中設定。ゲーム実録は2026年9月7日の開発記録で、Unityの実例とは扱わない。

費用は過去の2工程の例：Wan推定$0.56＋Tripo120 credits、1 credit=$0.01、1ドル160円で約282円。入力画像・再生成・開発エージェント等は除く。StudioとAPIは別契約・別クレジット。公式ページ画像の取得日時と出典はweb_refs_v3.jsonと概要欄へ記録する。

'''
script=script.replace('{new_count}',str(new_count)).replace('{len(rows)-new_count}',str(len(rows)-new_count))
script+='やめ太郎は「設計図」「同じ人の回転撮影」「ぬいぐるみの骨組み」「餅は餅屋」という例えで理解を助ける。たこさんは手2本＋足6本＝計8本。生成時は足8本（手を含め計10本）だったため余分な足を修正した。\n\n'
script+=f"タイムライン：{end/30:.3f}秒／1280×720／30fps。正本：`remotion/src/edit-manifest-v3.json`。\n\n"
chapter=None
for d in rows:
    if d['chapter']!=chapter:chapter=d['chapter'];script+='\n## '+chapter+'\n\n'
    script+=f"- {d['id']} {'やめ太郎' if d['who']=='yametaro' else 'たこさん'}「{d['text']}」\n  - 画面：`{d['view']}`\n"
script+='\n## 制作資料\n\n- `remotion/dialogue-v3.json`、`remotion/acting-plan-v3.json`、`voice_record_v3.json`\n- `web_refs_v3.json`、`review_v3.md`、`delivery_v3.json`\n- 公式3D：https://madogiwa.work/characters/sobaya\n- Wan解説：https://www.youtube.com/watch?v=RMWefLVS9vQ\n- 出典・クレジット：`youtube_description.txt`\n'
(P.parent/'script.md').write_text(script)
print('V3',end/30,'seconds',len(rows),'utterances')
