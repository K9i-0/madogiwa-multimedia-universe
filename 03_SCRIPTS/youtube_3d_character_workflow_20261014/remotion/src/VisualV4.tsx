import React from 'react';
import {Img, Loop, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {VisualV3} from './VisualV3';
import {ModelSceneV2} from './ModelSceneV2';

// V4 only replaces the comparison and resolution/cost guidance. All other views retain V3.
type Props = React.ComponentProps<typeof VisualV3>;
const C = {ink: '#15372a', green: '#176b47', light: '#e7f1eb', muted: '#51695c'};
const row: React.CSSProperties = {display: 'flex', alignItems: 'center'};
const Stage = ({title, children, source}: {title: string; children: React.ReactNode; source?: string}) =>
  <div style={{width: 1000, height: 470, display: 'flex', flexDirection: 'column', background: '#fff', color: C.ink, overflow: 'hidden'}}>
    <div style={{height: 49, flexShrink: 0, borderBottom: `2px solid ${C.green}`, fontSize: 31, fontWeight: 800, lineHeight: 1.25}}>{title}</div>
    <div style={{flex: 1, minHeight: 0, ...row, justifyContent: 'center'}}>{children}</div>
    {source && <div style={{height: 26, flexShrink: 0, padding: '3px 30px 0', fontSize: 17, lineHeight: 1.3, color: C.muted}}>{source}</div>}
  </div>;
const Label = ({children, dark = false}: {children: React.ReactNode; dark?: boolean}) =>
  <div style={{height: 45, boxSizing: 'border-box', ...row, padding: '7px 14px', fontSize: 23, fontWeight: 750,
    background: dark ? C.green : C.light, color: dark ? '#fff' : C.green}}>{children}</div>;

/** Match head-to-sole height rather than scaling the differently framed originals to equal boxes. */
const ComparisonImage = ({kind, width}: {kind: 'reference'|'blender'; width: number}) => {
  const height = 356, bodyHeight = 270, headTop = 44;
  if (kind === 'blender') {
    const scale = bodyHeight / (837 - 70);
    return <div style={{width, height, position: 'relative', overflow: 'hidden', background: '#f2f3f1'}}>
      <Img src={staticFile('old.jpg')} style={{position: 'absolute', width: 900 * scale, height: 900 * scale,
        maxWidth: 'none', left: (width - 900 * scale) / 2, top: headTop - 70 * scale}} />
    </div>;
  }
  // Current canonical sheet, central FRONT view. Historical submitted sheet stays untouched.
  const scale = bodyHeight / (614 - 62), crop = {x: 416, y: 50, width: 264, height: 580};
  return <div style={{width, height, position: 'relative', overflow: 'hidden', background: '#f2f3f1'}}>
    <div style={{position: 'absolute', width: crop.width * scale, height: crop.height * scale, overflow: 'hidden',
      left: (width - crop.width * scale) / 2, top: headTop - (62 - crop.y) * scale}}>
      <Img src={staticFile('sobaya_reference_v4.png')} style={{position: 'absolute', width: 1672 * scale, height: 941 * scale,
        maxWidth: 'none', left: -crop.x * scale, top: -crop.y * scale}} />
    </div>
  </div>;
};

function Comparison({t, id, complete}: {t: number; id?: string; complete: boolean}) {
  const width = complete ? 321 : 430;
  return <Stage title={complete ? '同じ「そば屋」で、ここまで変わる' : '基準のそば屋と、見比べると……'}>
    <div style={{display: 'flex', alignItems: 'flex-start', gap: complete ? 18 : 40}}>
      <div style={{width}}><Label>基準の画像</Label><ComparisonImage kind="reference" width={width} /></div>
      <div style={{width}}><Label>Blender版</Label><ComparisonImage kind="blender" width={width} /></div>
      {complete && <div style={{width}}><Label dark><Img src={staticFile('webrefs_v3/tripo_logo_white.svg')}
        style={{display: 'block', width: 117, height: 29, objectFit: 'contain'}} /><span style={{marginLeft: 12}}>→ 手直し</span></Label>
        <div style={{width, height: 356, overflow: 'hidden'}}><ModelSceneV2 t={t} kind="sobaya"
          mode={id === 'u008' || id === 'r009' ? 'turn' : 'greeting'} width={width} height={356} zoom={.90} /></div>
      </div>}
    </div>
  </Stage>;
}

function Portrait({t, id}: {t: number; id?: string}) {
  const frame = useCurrentFrame(), {fps} = useVideoConfig();
  const recommend = id === 't050' || id === 'u051';
  return <Stage title="3D用の回転素材は、細部を残す">
    <div style={{width: 1000, ...row, justifyContent: 'center', gap: 70}}>
      <div style={{width: 280, height: 374}}><Sequence from={frame - Math.round(t * fps)} layout="none">
        <Loop layout="none" durationInFrames={241}><OffthreadVideo muted src={staticFile('turn.mp4')}
          style={{display: 'block', width: 280, height: 374, objectFit: 'contain'}} /></Loop>
      </Sequence></div>
      <div style={{width: 510}}>
        <div style={{fontSize: 33, fontWeight: 800}}>制作例：720p</div>
        <div style={{fontSize: 23, color: C.muted, marginTop: 8}}>832 × 1108</div>
        <div style={{visibility: recommend ? 'visible' : 'hidden', marginTop: 30, padding: '21px 25px', background: C.light}}>
          <div style={{fontSize: 25}}>今から作るなら</div>
          <div style={{fontSize: 45, fontWeight: 850, color: C.green, marginTop: 7}}>1080p 推奨</div>
        </div>
      </div>
    </div>
  </Stage>;
}

/** Normal-price estimate for a new 1080p video; never relabels the historical 720p clip. */
function EstimatedPrices({view}: {view: string}) {
  const phase = ['cost', 'cost_video', 'cost_tripo', 'cost_total'].indexOf(view);
  const entries = [
    {title: '回転素材・8秒・1080p', logo: 'wan_logo.png', yen: '256円', usd: '$1.60', detail: '通常単価 $0.20 / 秒', logoHeight: 46},
    {title: '3D生成・今回の実例', logo: 'tripo_logo.svg', yen: '192円', usd: '$1.20', detail: 'Tripo・120 credits', logoHeight: 30},
  ];
  return <Stage title="1080pで作る場合の目安" source="通常価格の試算・1ドル160円。入力画像／再試行／Codex等は別。">
    <div style={{width: 1000}}>
      <div style={{display: 'flex', gap: 26}}>{entries.map((entry, i) => <div key={entry.logo}
        style={{width: 487, boxSizing: 'border-box', padding: '20px 26px', background: phase === i + 1 ? C.light : '#f5f7f5'}}>
        <div style={{fontSize: 25, fontWeight: 750}}>{entry.title}</div>
        <div style={{...row, justifyContent: 'space-between', height: 103, marginTop: 12}}>
          <Img src={staticFile(`webrefs_v3/${entry.logo}`)} style={{display: 'block', width: 120, height: entry.logoHeight, objectFit: 'contain'}} />
          <div style={{visibility: phase >= i + 1 ? 'visible' : 'hidden', textAlign: 'right'}}>
            <div style={{fontSize: 52, fontWeight: 850, color: C.green}}>{entry.yen}</div>
            <div style={{fontSize: 20, color: C.muted}}>{entry.usd}</div>
          </div>
        </div>
        <div style={{fontSize: 20, color: C.muted, visibility: phase >= i + 1 ? 'visible' : 'hidden'}}>{entry.detail}</div>
      </div>)}</div>
      {phase === 3 && <div style={{...row, justifyContent: 'space-between', marginTop: 18, padding: '14px 28px', background: C.green, color: '#fff'}}>
        <div style={{fontSize: 28, fontWeight: 800}}>2工程の合計</div><div style={{fontSize: 58, fontWeight: 850}}>448円</div>
      </div>}
    </div>
  </Stage>;
}

export function VisualV4(props: Props) {
  if (['cost', 'cost_video', 'cost_tripo', 'cost_total'].includes(props.view)) return <EstimatedPrices view={props.view} />;
  if (props.view === 'old') return <Comparison t={props.t} id={props.id} complete={false} />;
  if (props.view === 'sobaya_intro') return <Comparison t={props.t} id={props.id} complete />;
  if (props.view === 'portrait') return <Portrait t={props.t} id={props.id} />;
  return <VisualV3 {...props} />;
}
