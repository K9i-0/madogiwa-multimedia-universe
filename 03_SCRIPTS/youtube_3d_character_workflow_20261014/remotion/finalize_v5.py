"""Adopt the changed lines and build v5 from their measured durations."""
from pathlib import Path
import json, os, hashlib
P = Path(__file__).resolve().parent
rows = json.loads((P/'out/voice_progress_v5.json').read_text())
expected = json.loads((P/'dialogue-v5.json').read_text())
assert [r['id'] for r in rows] == [r['id'] for r in expected]
for generated, requested in zip(rows, expected):
    for key in ('who', 'text', 'chapter', 'view'):
        assert generated[key] == requested[key], f"Regenerate audio before adopting changed {requested['id']} {key}"
cursor = 12
for d in rows:
    if not d.get('reuseAudio'):
        src = P/'public'/d['audio']; name = f"clip_v5_{d['id']}_{d['who']}.wav"; dst = P.parent/name
        if not dst.exists(): dst.write_bytes(src.read_bytes())
        assert hashlib.sha256(dst.read_bytes()).hexdigest() == d['audioSha256']
        link = P/'public'/name
        if not link.exists(): link.symlink_to(os.path.relpath(dst, link.parent))
        d['audio'] = name
    d['startFrame'] = cursor
    cursor += d['durationInFrames'] + d.get('pause', 9)
end = cursor + 42
m = {'composition': {'width':1280,'height':720,'fps':30,'durationInFrames':end}, 'mainStartFrame':next(d['startFrame'] for d in rows if d['chapter'].startswith('2.')), 'endingStartFrame':next(d['startFrame'] for d in rows if d['chapter'].startswith('8.')), 'voiceModel':'Irodori Yametaro + VOICEVOX Chugoku Usagi', 'dialogue':rows, 'clips':[], 'creditsInDescription':True}
(P/'src/edit-manifest-v5.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
record=[]
for d in rows:
    r={k:d[k] for k in ('id','who','text','spoken','audio','audioSha256','durationInFrames','startFrame','sampleRate')}
    r['reusedFromV4']=bool(d.get('reuseAudio'))
    r['voiceSettings']={k:v for k,v in d['voiceSettings'].items() if k!='query'}
    if 'query' in d['voiceSettings']:r['savedQuerySha256']=hashlib.sha256(json.dumps(d['voiceSettings']['query'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    record.append(r)
(P.parent/'voice_record_v5.json').write_text(json.dumps({'subjectiveListening':False,'exactQueries':'remotion/src/edit-manifest-v5.json','lines':record},ensure_ascii=False,indent=2)+'\n')
new_count=sum(not d.get('reuseAudio') for d in rows)
script='''# Tripoで窓際族を3Dにする — 完成版v5

2026-10-15の追加フィードバックを反映。回転動画の生成・四方向の切り出し・Tripo生成・保存までCodexへ依頼する流れを明示。概要欄の制作リポジトリを渡す依頼例と、Wan/Tripo双方のAPI準備を紹介する。冒頭には基準のそば屋画像を並べ、Blender版・Tripo版との違いを直接比較する。回転素材の生成設定は制作例720pと、これから作る場合の1080p推奨を区別。ARの自宅ネタとスマホアプリへの展開の台詞を変更。画面上の文字を厳選し、Excel風の数式バー・セル番地を撤去。公式サービスのロゴと実ページを出典付きで紹介する。API監視の詳細は削り、準備・依頼・生成物の確認を説明。ゲームはUnityを一般例として紹介し、投稿者がFlutterエンジニアなのでFlutter Sceneでも動かしている実例へつなぐ。両者の表情と聞き手の反応を台詞ごとに指定する。

登場：やめ太郎（Irodori v4.1-Small、正典参照・seed7・CFG5）、たこさん（VOICEVOX中国うさぎ・ノーマル61、速度1.1・音高0）。新規{new_count}発話、v4から{len(rows)-new_count}発話を再利用。元版は保持。

そば屋の縦832×1108のWan回転動画、四方向入力、たこさんの前後2画像、採用モデルと修正資料は実素材。冒頭のBlender版制作担当は劇中設定。ゲーム実録は2026年9月7日の開発記録で、Unityの実例とは扱わない。

費用は推奨1080Pを選ぶ場合の試算：Wan 3.0通常料金$0.20/秒×8秒=$1.60（256円）＋Tripoのそば屋制作実例120 credits=$1.20（192円）、1ドル160円で合計448円、約450円。実際の回転動画は720Pであり、1080Pで生成した実績とは扱わない。入力画像・再生成・開発エージェント等は除く。StudioとAPIは別契約・別クレジット。公式ページ画像の取得日時と出典はweb_refs_v3.jsonと概要欄へ記録する。

'''
script=script.replace('{new_count}',str(new_count)).replace('{len(rows)-new_count}',str(len(rows)-new_count))
script+='やめ太郎は「設計図」「同じ人の回転撮影」「ぬいぐるみの骨組み」「餅は餅屋」という例えで理解を助ける。たこさんは手2本＋足6本＝計8本。生成時は足8本（手を含め計10本）だったため余分な足を修正した。\n\n'
script+=f"タイムライン：{end/30:.3f}秒／1280×720／30fps。正本：`remotion/src/edit-manifest-v5.json`。\n\n"
chapter=None
for d in rows:
    if d['chapter']!=chapter:chapter=d['chapter'];script+='\n## '+chapter+'\n\n'
    script+=f"- {d['id']} {'やめ太郎' if d['who']=='yametaro' else 'たこさん'}「{d['text']}」\n  - 画面：`{d['view']}`\n"
script+='\n## 制作資料\n\n- `remotion/dialogue-v5.json`、`remotion/acting-plan-v5.json`、`voice_record_v5.json`\n- `asset_sources_v4.json`、`resolution_source_v4.json`、`asr_record_v5.json`\n- `repository_handoff_v5.json`\n- `web_refs_v3.json`、`review_v5.md`、`delivery_v5.json`\n- 公式3D：https://madogiwa.work/characters/sobaya\n- Wan解説：https://www.youtube.com/watch?v=RMWefLVS9vQ\n- 出典・クレジット：`youtube_description.txt`\n'
(P.parent/'script.md').write_text(script)
print('V5',end/30,'seconds',len(rows),'utterances')
