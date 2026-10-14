import React from 'react';
import {Img, Loop, OffthreadVideo, Sequence, Freeze, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {ModelSceneV2 as ModelScene} from './ModelSceneV2';

/** V3: evidence and demonstrations carry the explanation; narration lives in captions. */
const C = {ink: '#15372a', green: '#176b47', light: '#e7f1eb', line: '#bacbc1', muted: '#51695c', red: '#b4473b'};
const row: React.CSSProperties = {display: 'flex', alignItems: 'center'};
const centre: React.CSSProperties = {...row, justifyContent: 'center'};
const brandAssets: Record<string, string> = {
  Tripo: 'webrefs_v3/tripo_logo.svg', Codex: 'webrefs_v3/openai_icon.svg',
  'Claude Code': 'webrefs_v3/claude_logo.svg', Cursor: 'webrefs_v3/cursor_icon.svg',
  Wan: 'webrefs_v3/wan_logo.png', MiniMax: 'webrefs_v3/minimax_logo.webp',
  Blender: 'webrefs_v3/blender_logo.png', 'Three.js': 'webrefs_v3/threejs_icon.svg',
  Flutter: 'webrefs_v3/flutter_icon.svg', Remotion: 'webrefs_v3/remotion_icon.png',
  Unity: 'webrefs_v3/unity_logo.png',
};

const Pic = ({src, width, height, fit = 'contain'}: {src: string; width: number; height: number; fit?: 'contain'|'cover'}) =>
  <Img src={staticFile(src)} style={{display: 'block', width, height, objectFit: fit}} />;
const Label = ({children, dark = false}: {children: React.ReactNode; dark?: boolean}) =>
  <div style={{fontSize: 23, fontWeight: 700, padding: '8px 15px', background: dark ? C.green : C.light,
    color: dark ? '#fff' : C.green, lineHeight: 1.25}}>{children}</div>;
const Arrow = () => <div style={{fontSize: 40, color: C.green, padding: '0 14px'}}>→</div>;
const Word = ({children, size = 34}: {children: React.ReactNode; size?: number}) =>
  <div style={{fontSize: size, fontWeight: 800, lineHeight: 1.45}}>{children}</div>;
const Brand = ({name, size = 64, label = true}: {name: string; size?: number; label?: boolean}) =>
  <div style={{...centre, flexDirection: 'column', gap: 12}}>
    {brandAssets[name] && <Pic src={brandAssets[name]} width={['Tripo', 'Wan', 'Blender', 'Claude Code', 'Unity'].includes(name) ? size * 2 : size} height={name === 'Tripo' ? size / 2 : name === 'Wan' ? size * .76 : name === 'Blender' ? size * .62 : name === 'Claude Code' ? size * .44 : name === 'Unity' ? size * .68 : size} />}
    {label && !['Tripo', 'Wan', 'Blender', 'Unity'].includes(name) && <div style={{fontSize: 27, fontWeight: 750, whiteSpace: 'nowrap'}}>{name}</div>}
  </div>;
const Stage = ({title, children, source}: {title: string; children: React.ReactNode; source?: React.ReactNode}) =>
  <div style={{width: 1000, height: 470, display: 'flex', flexDirection: 'column', background: '#fff', color: C.ink, overflow: 'hidden'}}>
    <div style={{height: 49, flexShrink: 0, borderBottom: `2px solid ${C.green}`, fontSize: 31, fontWeight: 800, lineHeight: 1.25}}>{title}</div>
    <div style={{flex: 1, minHeight: 0, position: 'relative', ...centre}}>{children}</div>
    {source && <div style={{height: 26, flexShrink: 0, padding: '3px 30px 0', fontSize: 17, lineHeight: 1.3, color: C.muted}}>{source}</div>}
  </div>;

/** Crop actual evidence; never synthesize comparison images. */
const Crop = ({src, natural, crop, width, height}: {src: string; natural: [number, number]; crop: [number, number, number, number]; width: number; height: number}) => {
  const scale = Math.max(width / crop[2], height / crop[3]);
  return <div style={{position: 'relative', width, height, overflow: 'hidden', flexShrink: 0}}>
    <Img src={staticFile(src)} style={{position: 'absolute', width: natural[0] * scale, height: natural[1] * scale,
      maxWidth: 'none', left: -crop[0] * scale + (width - crop[2] * scale) / 2,
      top: -crop[1] * scale + (height - crop[3] * scale) / 2}} />
  </div>;
};
const Model = ({t, width = 700, height = 402, ...props}: {t: number; width?: number; height?: number;
  kind?: 'sobaya'|'takosan'|'fukuchan'; mode?: string; close?: boolean; bones?: boolean; zoom?: number; freeze?: boolean}) =>
  <div style={{width, height, flexShrink: 0, overflow: 'hidden'}}><ModelScene t={t} width={width} height={height} {...props} /></div>;
const Turn = ({t, width = 295, height = 394}: {t: number; width?: number; height?: number}) => {
  const frame = useCurrentFrame(), {fps} = useVideoConfig();
  return <Sequence from={frame - Math.round(t * fps)} layout="none"><Loop layout="none" durationInFrames={241}>
    <OffthreadVideo muted src={staticFile('turn.mp4')} style={{display: 'block', width, height, objectFit: 'contain'}} />
  </Loop></Sequence>;
};
const TinyViews = ({width = 100, height = 133}: {width?: number; height?: number}) =>
  <div style={{display: 'grid', gridTemplateColumns: `${width}px ${width}px`, gap: 7}}>
    {['front', 'left', 'back', 'right'].map(v => <Pic key={v} src={`sobaya_${v}.png`} width={width} height={height} />)}
  </div>;

function Pipeline({t, active = -1}: {t: number; active?: number}) {
  const steps = [
    {name: '姿をそろえる', visual: <Pic src="sheet.png" width={232} height={276} />},
    {name: '3Dにする', visual: <TinyViews width={88} height={128} />},
    {name: '手直し', visual: <Model t={t} mode="greeting" bones width={232} height={276} />},
    {name: '作品へ', visual: <Pic src="game.png" width={232} height={276} />},
  ];
  return <div style={{display: 'flex', gap: 16}}>{steps.map((step, i) => <div key={step.name}
    style={{width: 238, position: 'relative', opacity: active === -1 || i <= active ? 1 : .25}}>
    <div style={{height: 285, ...centre}}>{step.visual}</div>
    <div style={{fontSize: 26, fontWeight: 800, textAlign: 'center', padding: '12px 0',
      borderTop: `3px solid ${i === active ? C.green : C.line}`}}>{step.name}</div>
    {i < 3 && <div style={{position: 'absolute', right: -22, top: 128, fontSize: 32, color: C.green}}>→</div>}
  </div>)}</div>;
}

function Prices({view, localT, id}: {view: string; localT: number; id?: string}) {
  const phase = ['cost', 'cost_video', 'cost_tripo', 'cost_total'].indexOf(view);
  const shown = (i: number) => phase > i + 1 || (phase === i + 1 && (id === ['u068', 'u069'][i] ? localT >= [9.42, 8.44][i] : true));
  const usd = (i: number) => phase > i + 1 || (phase === i + 1 && (id === ['u068', 'u069'][i] ? localT >= [4.24, 4.51][i] : true));
  return <Stage title="そば屋の生成費用" source="1ドル＝160円換算。動画は推定。入力画像・再試行・Codex等は別。">
    <div style={{width: 1000}}>
      <div style={{display: 'flex', gap: 26}}>{[['Wan', '回転動画・8秒', '約90円', '$0.56'], ['Tripo', '3D生成・120 credits', '約192円', '1 credit = $0.01']].map(([name, sub, price, dollar], i) =>
        <div key={name} style={{width: 487, padding: '20px 26px', boxSizing: 'border-box', background: phase === i + 1 ? C.light : '#f5f7f5'}}>
          <div style={{fontSize: 25, fontWeight: 750}}>{sub}</div>
          <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 16}}>
            <Brand name={name} size={60} />
            <div style={{textAlign: 'right'}}><div style={{fontSize: 52, fontWeight: 850, color: C.green, visibility: shown(i) ? 'visible' : 'hidden'}}>{price}</div>
              <div style={{fontSize: 19, color: C.muted, visibility: usd(i) ? 'visible' : 'hidden'}}>{dollar}</div></div>
          </div>
        </div>)}
      </div>
      {phase === 3 && <div style={{...row, justifyContent: 'space-between', padding: '14px 28px', marginTop: 18, background: C.green, color: '#fff'}}>
        <Word size={28}>2工程の合計</Word><Word size={60}>約282円</Word>
      </div>}
    </div>
  </Stage>;
}

function Plans({text, id, localT}: {text: string; id?: string; localT: number}) {
  const separate = id === 'r031' && localT >= 5.1;
  const api = id === 'r027' ? localT >= 5.0 : id === 'r031' || id === 'u026' ? false : /API|クレジット/.test(text);
  if (separate) return <Stage title="StudioとAPIは、別契約" source="tripo3d.ai/pricing　｜　developers.tripo3d.ai/en/pricing">
    <div style={{width: 1000, ...centre, gap: 90}}>{['Studio', 'API'].map(name => <div key={name} style={{width: 360, textAlign: 'center', borderTop: `4px solid ${C.green}`, padding: '35px 20px', background: C.light}}>
      <Brand name="Tripo" size={85} /><div style={{marginTop: 28}}><Word size={46}>{name}</Word></div>
    </div>)}</div>
  </Stage>;
  return <Stage title={api ? 'APIは、使った分をクレジットで' : 'ブラウザで使うなら、Studio'} source={api ? 'developers.tripo3d.ai/en/pricing　｜　2026.10.14' : 'tripo3d.ai/pricing　｜　月払い・USD　｜　2026.10.14'}>
    <div style={{width: 1000, ...row, gap: 24}}>
      <Pic src={api ? 'webrefs_v3/tripo_api_pricing_crop.png' : 'webrefs_v3/tripo_studio_monthly_crop.png'} width={738} height={374} />
      <div style={{width: 238}}><Brand name="Tripo" size={78} /><div style={{marginTop: 28, textAlign: 'center'}}>
        <Word>{api ? 'API' : 'Studio'}</Word><div style={{fontSize: 24, marginTop: 10}}>{api ? '従量課金' : '月額・年額'}</div>
      </div></div>
    </div>
  </Stage>;
}

// Hold source 18.000 seconds, before character loading starts at 18.2667 seconds.
const SiteCrop = ({from}: {from: number}) => {
  const frame = useCurrentFrame();
  return <Sequence from={from} layout="none"><Freeze frame={390} active={frame - from >= 390}>
    <OffthreadVideo muted src={staticFile('site_demo.mp4')} trimBefore={150}
      style={{display: 'block', position: 'absolute', width: 1024, height: 720, left: -190, top: -180}} />
  </Freeze></Sequence>;
};
function Site({t}: {t: number}) {
  const frame = useCurrentFrame(), {fps} = useVideoConfig();
  return <Stage title="公式サイトで、触れます" source="madogiwa.work/characters/sobaya　｜　概要欄へ">
    <div style={{width: 1000, ...row, gap: 28}}>
      <div style={{width: 706, height: 370, position: 'relative', overflow: 'hidden'}}><SiteCrop from={frame - Math.round(t * fps)} /></div>
      <div style={{width: 266}}><Word>回す<br />動かす</Word>
        <div style={{marginTop: 30, borderTop: `2px solid ${C.green}`, paddingTop: 15, fontSize: 18}}>そば屋の動作選択</div>
        <div style={{marginTop: 10}}><Crop src="site_3d.png" natural={[1280, 900]} crop={[660, 746, 300, 50]} width={266} height={44} /></div>
      </div>
    </div>
  </Stage>;
}
function Game({t}: {t: number}) {
  const frame = useCurrentFrame(), {fps} = useVideoConfig();
  return <Stage title="窓際族物語では、Flutter Scene" source="そば屋ハザード 開発記録｜2026.09.07・当時のモデル">
    <div style={{width: 1000, ...row, gap: 28}}>
      <div style={{width: 658, height: 370, position: 'relative', overflow: 'hidden'}}>
        <Sequence from={frame - Math.round(t * fps)} layout="none"><OffthreadVideo muted src={staticFile('game_demo_v2.mp4')}
          style={{display: 'block', width: 658, height: 370, objectFit: 'contain'}} /></Sequence>
      </div>
      <div style={{width: 314, textAlign: 'center'}}><Brand name="Flutter" size={105} />
        <div style={{fontSize: 23, marginTop: 30, lineHeight: 1.6}}>投稿者は<br /><b>Flutterエンジニア</b></div>
      </div>
    </div>
  </Stage>;
}

export function VisualV3({view, t, text = '', localT = 0, id}: {view: string; t: number; text?: string; localT?: number; id?: string}) {
  if (['cost', 'cost_video', 'cost_tripo', 'cost_total'].includes(view)) return <Prices view={view} localT={localT} id={id} />;
  if (view === 'opening') return <Stage title="このキャラも、3Dにできる？">
    <div style={{width: 1000, ...centre, gap: 80}}><Pic src="sobaya_front.png" width={390} height={405} />
      <div><Word size={53}>画像1枚から<br />自分のキャラへ。</Word></div></div>
  </Stage>;
  if (view === 'old') return <Stage title="Codexが作った、そば屋さん">
    <div style={{width: 1000, ...centre, gap: 55}}><Pic src="old.jpg" width={410} height={405} />
      <Word size={46}>{/誰|感想/.test(text) ? <>誰かは、<br />伝わる。</> : <>特徴は<br />拾ってる……？</>}</Word></div>
  </Stage>;
  if (view === 'sobaya_intro') return <Stage title="同じ「そば屋」で、ここまで変わる">
    <div style={{display: 'flex', width: 1000, gap: 18, alignItems: 'center'}}>
      <div style={{width: 310}}><Label>Blenderで制作</Label><Pic src="old.jpg" width={310} height={350} /></div>
      <Arrow /><div style={{width: 586}}><div style={{...row, gap: 16, background: C.green, padding: '8px 15px'}}><Pic src="webrefs_v3/tripo_logo_white.svg" width={132} height={32} /><div style={{color: '#fff', fontSize: 23, fontWeight: 750}}>→ 手直し</div></div>
        <Model t={t} mode={id === 'u008' || id === 'r009' ? 'turn' : 'greeting'} width={586} height={350} /></div>
    </div>
  </Stage>;
  if (view === 'hosts') return <Stage title="窓際族物語の3D制作ノート">
    <div style={{width: 1000, ...centre, gap: 80}}><Word size={54}>やめ太郎</Word><span style={{fontSize: 42, color: C.line}}>＆</span><Word size={54}>たこさん</Word></div>
  </Stage>;
  if (view === 'promise' || view === 'uses') return <Stage title="一体を、いろんな作品へ">
    <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px 28px', width: 1000}}>
      {[{name: 'Web', src: 'site_3d.png'}, {name: '動画', model: true}, {name: 'AR', src: 'ar.png'}, {name: 'ゲーム', src: 'game.png'}].map(x =>
        <div key={x.name} style={{...row, gap: 20, borderBottom: `1px solid ${C.line}`, height: 184}}>
          {x.model ? <Model t={t} mode="greeting" width={278} height={180} /> : <Pic src={x.src!} width={278} height={180} />}
          <Word size={32}>{x.name}</Word>
        </div>)}
    </div>
  </Stage>;
  if (view === 'pipeline') return <Stage title="完成までの4工程"><Pipeline t={t} active={id === 'r023' ? (localT < 1.68 ? -2 : [1.68, 3.30, 5.33, 8.32].filter(n => localT >= n).length - 1) : -1} /></Stage>;
  if (view === 'tripo') return <Stage title="画像から3Dを作る、Tripo" source="tripo3d.ai">
    <div style={{width: 1000, ...centre, gap: 20}}><Pic src="sobaya_front.png" width={240} height={375} /><Arrow />
      <Brand name="Tripo" size={90} /><Arrow /><Model t={t} mode="turn" width={360} height={375} />
    </div>
  </Stage>;
  if (view === 'cost_time') return <Stage title="サービス代と、作業時間">
    <div style={{width: 1000, ...centre, gap: 35}}>
      <div style={{background: C.light, padding: '38px 48px'}}><Word size={41}>サービス代</Word></div>
      <Word size={50}>＋</Word><div style={{borderBottom: `5px solid ${C.green}`, padding: '38px 34px'}}><Word size={41}>試行・確認の時間</Word></div>
    </div>
  </Stage>;
  if (view === 'roles') return <Stage title="餅は餅屋。作業を分ける">
    <div style={{width: 1000, ...centre, gap: 30}}><div style={{textAlign: 'center'}}><Brand name="Tripo" size={85} /><Word size={31}>原型を作る</Word></div>
      <Model t={t} mode="greeting" width={400} height={400} />
      <div style={{textAlign: 'center'}}><div style={{...row, gap: 20}}><Brand name="Codex" size={65} /><Brand name="Blender" size={65} /></div><div style={{marginTop: 20}}><Word size={31}>整えて使う</Word></div></div>
    </div>
  </Stage>;
  if (view === 'plans') return <Plans text={text} id={id} localT={localT} />;
  if (view === 'api' || view === 'config' || view === 'tasks') return <Stage title="いつものCodexから、Tripoへ">
    <div style={{width: 1000, ...centre, gap: 45}}><Brand name="Codex" size={105} /><Arrow /><Brand name="Tripo" size={105} /><Arrow />
      <div><Word size={45}>GLB</Word><div style={{fontSize: 23, marginTop: 8}}>3Dモデル</div></div>
    </div>
  </Stage>;
  if (view === 'setup') return <Stage title="APIの準備は、最初に一度">
    <div style={{width: 1000, ...centre, gap: 70}}><Brand name="Tripo" size={110} /><Arrow />
      <div style={{display: 'flex', gap: 24}}>{['APIキー', 'クレジット'].map((s, i) => <div key={s} style={{width: 245, padding: '35px 15px', textAlign: 'center', background: C.light}}>
        <div style={{fontSize: 22, color: C.green, marginBottom: 15}}>0{i + 1}</div><Word>{s}</Word>
      </div>)}</div>
    </div>
  </Stage>;
  if (view === 'codex_request') return <Stage title="Codexへの指示例" source="概要欄の制作リポジトリを開いて実行">
    <div style={{width: 940, borderLeft: `7px solid ${C.green}`, background: C.light, padding: '40px 35px', boxSizing: 'border-box'}}>
      <div style={{fontSize: 35, fontWeight: 750, lineHeight: 1.65}}>4方向の画像を使ってTripoで3Dを生成して。<br />完了したらGLBを保存して。</div>
    </div>
  </Stage>;
  if (view === 'ai_handoff') return <Stage title="人は、できた形を確かめる">
    <div style={{width: 1000, ...row, gap: 30}}><div style={{width: 240, textAlign: 'center'}}><Brand name="Codex" size={95} /><div style={{marginTop: 25}}><Word>生成・保存</Word></div></div>
      <Arrow /><Model t={t} mode="turn" width={355} height={400} />
      <div style={{width: 240, borderLeft: `4px solid ${C.green}`, paddingLeft: 20}}><div style={{fontSize: 23, color: C.muted, marginBottom: 13}}>人が確認</div><Word>形<br />使い道</Word></div>
    </div>
  </Stage>;
  if (view === 'agents') return <Stage title="使い慣れたAIツールから">
    <div style={{width: 1000, ...centre, gap: 30}}>{['Codex', 'Claude Code', 'Cursor'].map(name => <div key={name} style={{width: 195}}><Brand name={name} size={93} /></div>)}
      <Arrow /><Brand name="Tripo" size={105} />
    </div>
  </Stage>;
  if (view === 'sheet') return <Stage title="キャラクターシートを基準に"><Pic src="sheet.png" width={1000} height={405} /></Stage>;
  if (view === 'turn') return <Stage title="同じ姿から、向きをそろえる">
    <div style={{width: 1000, ...centre, gap: 28}}><Turn t={t} /><Arrow /><div style={{display: 'flex', gap: 10}}>
      {['front', 'left', 'back', 'right'].map(v => <Pic key={v} src={`sobaya_${v}.png`} width={137} height={290} />)}
    </div></div>
  </Stage>;
  if (view === 'consistency') return <Stage title="向きが変わっても、同じ姿？">
    <div style={{width: 1000, ...row, gap: 38}}><div style={{display: 'flex', gap: 14}}>
      {['front', 'left', 'back'].map(v => <Pic key={v} src={`sobaya_${v}.png`} width={204} height={360} />)}
    </div><div style={{borderLeft: `3px solid ${C.green}`, paddingLeft: 28}}><Word>顔・髪<br />体格<br />衣装</Word></div></div>
  </Stage>;
  if (view === 'portrait') return <Stage title="全身を、大きく収める">
    <div style={{width: 1000, ...centre, gap: 75}}><Turn t={t} /><div><Word size={54}>832 × 1108</Word><div style={{fontSize: 27, marginTop: 22}}>この例は、縦長・8秒</div></div></div>
  </Stage>;
  if (view === 'views') {
    const active = /時間だけ|向き|2秒|二秒/.test(text) ? -1 : Math.min(3, Math.floor(t / 1.8));
    return <Stage title="時刻より、向きで選ぶ">
      <div style={{display: 'flex', gap: 16}}>{['front', 'left', 'back', 'right'].map((v, i) => <div key={v} style={{width: 238,
        border: `3px solid ${i === active ? C.green : 'transparent'}`, boxSizing: 'border-box'}}>
        <Pic src={`sobaya_${v}.png`} width={232} height={313} />
        <div style={{...row, justifyContent: 'space-between', padding: '8px 10px', fontSize: 23, background: i === active ? C.green : C.light, color: i === active ? '#fff' : C.ink}}>
          <b>{['正面', '左', '背面', '右'][i]}</b><span>{['0.2', '2.5', '4.0', '5.6'][i]}秒</span>
        </div>
      </div>)}</div>
    </Stage>;
  }
  if (view === 'tako_views') return <Stage title="たこさんは、正面と背面から">
    <div style={{width: 1000, ...centre, gap: 55}}>{[['takosan_front.png', '正面'], ['takosan_back.png', '背面']].map(([src, label]) =>
      <div key={src}><Label>{label}</Label><Pic src={src} width={380} height={352} /></div>)}</div>
  </Stage>;
  if (view === 'tako_fix') return <Stage title="足の本数を直す">
    <div style={{width: 1000, ...row, gap: 24}}><Model kind="takosan" t={t} mode="float" zoom={.90} width={600} height={405} />
      <div style={{width: 376}}><div style={{...row, gap: 8, justifyContent: 'center'}}>
        <div style={{textAlign: 'center'}}><div style={{fontSize: 21}}>生成時の足</div><Word size={74}>8本</Word></div><Arrow />
        <div style={{textAlign: 'center', color: C.green}}><div style={{fontSize: 21}}>手直し後の足</div><Word size={74}>6本</Word></div>
      </div><div style={{fontSize: 25, textAlign: 'center', marginTop: 22, paddingTop: 18, borderTop: `2px solid ${C.line}`}}>手2本は、そのまま</div></div>
    </div>
  </Stage>;
  if (view === 'takosan_intro' || view === 'tako_bones') return <Stage title={view === 'tako_bones' ? 'この体に合う、動かし方' : 'たこさんも、3Dに'}>
    <div style={{width: 1000, ...row, gap: 40}}><Model kind="takosan" t={t} mode="float" zoom={.90} bones={view === 'tako_bones'} width={700} height={405} />
      {view === 'tako_bones' ? <Word size={34}>6本の足<br />× 3関節</Word> : <div style={{width: 260}}><Word size={28}>手2本 ＋ 足6本</Word><div style={{borderTop: `2px solid ${C.green}`, paddingTop: 18, marginTop: 18}}><Word size={55}>計8本</Word></div></div>}</div>
  </Stage>;
  if (view === 'blender') return <Stage title="Blenderで、姿勢を整える">
    <div style={{width: 1000, ...centre, gap: 35}}>{[['posture_before.png', '修正前'], ['posture_after.png', '修正後']].map(([src, label], i) =>
      <React.Fragment key={src}>{i > 0 && <Arrow />}<div><Label dark={i === 1}>{label}</Label><Pic src={src} width={380} height={352} /></div></React.Fragment>)}</div>
  </Stage>;
  if (view === 'face_fix') {
    if (localT < 6.4) return <Stage title="仮面も、本人らしく" source="顔パーツの修正記録">
      <div style={{width: 1000, display: 'flex', gap: 20}}>{[{x: 683, label: '修正前'}, {x: 1365, label: '修正後'}].map((s, i) =>
        <div key={s.label} style={{width: 490}}><Label dark={i === 1}>{s.label}</Label><div style={{...centre, background: '#f0f2ef'}}>
          <Crop src="face_compare.png" natural={[2048, 897]} crop={[s.x, 58, 682, 839]} width={276} height={340} /></div></div>)}</div>
    </Stage>;
    return <Stage title="光沢や傾きも、仕上げる"><Model t={t} mode="face" close zoom={1.12} width={1000} height={405} /></Stage>;
  }
  if (view === 'fuku') return <Stage title="福ギュン：「本人らしさ」が難しい">
    <div style={{width: 1000, display: 'flex', gap: 18}}><div style={{width: 400}}><Label>参照写真</Label>
      <Crop src="fuku_photo.jpg" natural={[1378, 2356]} crop={[230, 0, 900, 740]} width={400} height={352} /></div>
      <div style={{width: 582}}><Label dark>手直し後の3D</Label><Model kind="fukuchan" t={t} mode="face" close zoom={1.25} width={582} height={352} /></div>
    </div>
  </Stage>;
  if (view === 'rig_compare') return <Stage title="「回す」と「曲げる」">
    <div style={{width: 1000, display: 'flex', gap: 18}}><div><Label>全体を回す</Label><Model t={t} mode="turn" freeze width={491} height={352} /></div>
      <div><Label dark>関節を曲げる</Label><Model t={t} mode="greeting" bones width={491} height={352} /></div></div>
  </Stage>;
  if (view === 'rig') {
    const weight = id === 'r096', named = weight ? localT >= 6.49 : id === 'r094' ? localT >= 3.30 : true;
    return <Stage title={weight ? '骨に、表面がついてくる' : '腕や脚を、曲げられるように'}>
      <div style={{width: 1000, ...row, gap: 38}}><Model t={t} mode="greeting" bones width={720} height={405} />
        <div style={{width: 242, color: weight ? C.green : C.red}}><Word size={42}>{named ? (weight ? 'ウェイト' : 'リグ') : '骨格'}</Word></div></div>
    </Stage>;
  }
  if (view === 'weights') {
    const pelvis = localT >= 4.33;
    return <Stage title={pelvis ? '脚を開いたときの、形' : '腕を上げたときの、形'} source="同じモーション・同じ時刻の比較">
      <div style={{width: 1000, display: 'flex', gap: 20}}>{[{x: pelvis ? 0 : 640, label: '修正前'}, {x: pelvis ? 320 : 960, label: '修正後'}].map((s, i) =>
        <div key={s.label}><Label dark={i === 1}>{s.label}</Label><Crop src={pelvis ? 'pelvis.png' : 'weights.png'} natural={pelvis ? [1280, 2070] : [1280, 1380]}
          crop={[s.x, pelvis ? 370 : 25, 320, 320]} width={490} height={340} /></div>)}</div>
    </Stage>;
  }
  if (view === 'wan_link') return <Stage title="Wanの詳しい手順は、公開済み動画へ">
    <div style={{width: 1000, ...row, gap: 40}}><Pic src="wan_thumbnail.png" width={690} height={388} /><Word size={32}>概要欄に<br />リンク</Word></div>
  </Stage>;
  if (view === 'video_models') return <Stage title="回転動画は、使い慣れた方法で">
    <div style={{width: 1000, ...centre, gap: 75}}><Turn t={t} /><div style={{width: 480}}>
      <div style={{...row, gap: 32, background: C.light, padding: '24px 30px'}}><Brand name="Wan" size={85} /><Word size={29}>今回の制作</Word></div>
      <div style={{...row, gap: 18, marginTop: 23, paddingLeft: 20}}><Pic src="webrefs_v3/minimax_logo.webp" width={190} height={70} /><Word size={31}>H3</Word><span style={{fontSize: 25}}>など</span></div>
    </div></div>
  </Stage>;
  if (view === 'website') return <Site t={t} />;
  if (view === 'ar') return <Stage title="ARで、いつもの空間へ" source="madogiwa.work/camera/sobaya　｜　実際の準備画面">
    <div style={{width: 1000, ...centre, gap: 85}}><Crop src="ar_v2.png" natural={[430, 1246]} crop={[20, 715, 390, 430]} width={342} height={377} />
      <div><Word size={58}>AR</Word><div style={{fontSize: 31, marginTop: 24, lineHeight: 1.6}}>部屋に置く<br />一緒に撮る</div></div></div>
  </Stage>;
  if (view === 'game_unity' || view === 'unity' || view === 'game_engines') return <Stage title="ゲームエンジンにも、持ち込める">
    <div style={{width: 1000, ...centre, gap: 50}}><Model t={t} mode="walk" width={520} height={405} /><Arrow />
      <div style={{width: 300, textAlign: 'center'}}><Brand name="Unity" size={124} /><div style={{fontSize: 24, marginTop: 22}}>ゲームエンジンの例</div></div>
    </div>
  </Stage>;
  if (view === 'game') return <Game t={t} />;
  if (view === 'three') return <Stage title="Three.jsで、Webへ">
    <div style={{width: 1000, ...row, gap: 35}}><Model t={t} mode="greeting" width={710} height={405} /><div style={{width: 255}}><Brand name="Three.js" size={115} /></div></div>
  </Stage>;
  if (view === 'remotion') {
    const close = /寄った/.test(text) ? localT >= 3.2 : /カメラ|顔が変わ|範囲/.test(text), walk = /別の動画/.test(text);
    const demoT = id === 'u110' ? Math.max(0, localT - 1.3) : t, mode = id === 'u110' && localT < 1.3 ? 'idle' : walk ? 'walk' : 'greeting';
    return <Stage title="この動画も、同じ3Dモデル">
      <div style={{width: 1000, position: 'relative'}}><Model t={demoT} mode={mode} close={close} width={1000} height={405} />
        <div style={{position: 'absolute', top: 20, left: 25, fontSize: 24, fontWeight: 750, background: '#fff', padding: '9px 16px', borderLeft: `4px solid ${C.green}`}}>
          {close ? 'カメラ' : walk ? '動作' : '手を振る'}
        </div>
        <div style={{position: 'absolute', right: 26, top: 27}}><Brand name="Remotion" size={64} /></div>
      </div>
    </Stage>;
  }
  if (view === 'links') return <Stage title="完成モデルは、公式サイトへ">
    <div style={{width: 1000, ...centre, gap: 45}}><Model t={t} mode="greeting" width={500} height={405} />
      <div><Word size={44}>madogiwa.work</Word><div style={{fontSize: 28, marginTop: 25, color: C.green}}>概要欄から</div></div></div>
  </Stage>;
  if (view === 'ending') return <Stage title="まずは一体、動かしてみる">
    <div style={{position: 'relative', width: 1000, height: 405}}><Model t={id === 'u127' ? t - localT : t} mode="idle" width={1000} height={405} />
      {(id !== 'u125' || localT >= .7) && <div style={{position: 'absolute', right: 35, top: 28, background: '#fff', borderLeft: `5px solid ${C.green}`, padding: '13px 18px', fontSize: 24, fontWeight: 750}}>出勤中 <span style={{fontSize: 20, color: C.muted}}>（表示のみ）</span></div>}
    </div>
  </Stage>;
  if (view === 'greeting' || view === 'walk' || view === 'sobaya_raw') return <Stage title={view === 'greeting' ? '動かして、確かめる' : view === 'walk' ? '形から、動きへ' : '原型から、動くモデルへ'}>
    <Model t={t} mode={view === 'walk' ? 'walk' : 'greeting'} width={1000} height={405} />
  </Stage>;
  return <Stage title="完成までの4工程"><Pipeline t={t} /></Stage>;
}
