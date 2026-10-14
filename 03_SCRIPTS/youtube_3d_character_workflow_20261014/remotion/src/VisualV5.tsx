import React from 'react';
import {Img, Loop, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {VisualV4} from './VisualV4';

// V5 clarifies how much of the preparation Codex can carry out from one request.
type Props = React.ComponentProps<typeof VisualV4>;
const C = {ink: '#15372a', green: '#176b47', light: '#e7f1eb', muted: '#51695c', line: '#bacbc1'};
const row: React.CSSProperties = {display: 'flex', alignItems: 'center'};
const centre: React.CSSProperties = {...row, justifyContent: 'center'};
const Pic = ({src, width, height}: {src: string; width: number; height: number}) =>
  <Img src={staticFile(src)} style={{display: 'block', width, height, objectFit: 'contain'}} />;
const Stage = ({title, children}: {title: string; children: React.ReactNode}) =>
  <div style={{width: 1000, height: 470, display: 'flex', flexDirection: 'column', background: '#fff', color: C.ink, overflow: 'hidden'}}>
    <div style={{height: 49, flexShrink: 0, borderBottom: `2px solid ${C.green}`, fontSize: 31, fontWeight: 800, lineHeight: 1.25}}>{title}</div>
    <div style={{flex: 1, minHeight: 0, ...centre}}>{children}</div>
  </div>;
const Codex = ({size = 38}: {size?: number}) => <div style={{...row, gap: 13}}>
  <Pic src="webrefs_v3/openai_icon.svg" width={size} height={size} />
  <span style={{fontSize: 26, fontWeight: 750}}>Codex</span>
</div>;

function Turn({t}: {t: number}) {
  const frame = useCurrentFrame(), {fps} = useVideoConfig();
  return <Sequence from={frame - Math.round(t * fps)} layout="none">
    <Loop layout="none" durationInFrames={241}><OffthreadVideo muted src={staticFile('turn.mp4')}
      style={{display: 'block', width: 172, height: 230, objectFit: 'contain'}} /></Loop>
  </Sequence>;
}

function DelegatedWorkflow({t}: {t: number}) {
  const steps = [
    {name: '回転動画を生成', visual: <Turn t={t} />},
    {name: '4方向を切り出す', visual: <div style={{display: 'grid', gridTemplateColumns: '82px 82px', gap: 7}}>
      {['front', 'left', 'back', 'right'].map(v => <Pic key={v} src={`sobaya_${v}.png`} width={82} height={109} />)}
    </div>},
    {name: 'Tripoで3D生成', visual: <div style={{...centre, flexDirection: 'column', gap: 33}}>
      <Pic src="webrefs_v3/tripo_logo.svg" width={185} height={47} />
      <div style={{border: `2px solid ${C.line}`, padding: '15px 30px', fontSize: 37, fontWeight: 800, background: '#fff'}}>GLB</div>
    </div>},
  ];
  return <Stage title="動画から3Dまで、Codexに任せる">
    <div style={{width: 960, border: `2px solid ${C.line}`, boxSizing: 'border-box'}}>
      <div style={{...centre, height: 54, background: C.light}}><Codex size={32} /></div>
      <div style={{display: 'flex', padding: '16px 14px 15px', gap: 40}}>{steps.map((step, i) =>
        <div key={step.name} style={{width: 282, position: 'relative', flexShrink: 0}}>
          <div style={{height: 230, ...centre}}>{step.visual}</div>
          <div style={{fontSize: 26, fontWeight: 800, textAlign: 'center', marginTop: 13}}>{step.name}</div>
          {i < 2 && <div style={{position: 'absolute', right: -35, top: 94, fontSize: 39, color: C.green}}>→</div>}
        </div>)}</div>
    </div>
  </Stage>;
}

function RepositoryRequest() {
  return <Stage title="Codexへの依頼例">
    <div style={{width: 940}}>
      <div style={{...row, justifyContent: 'space-between', marginBottom: 18}}>
        <Codex />
        <div style={{fontSize: 23, color: C.green, background: C.light, padding: '12px 20px', fontWeight: 700}}>窓際族リポジトリ｜概要欄から</div>
      </div>
      <div style={{...row, gap: 32, padding: '22px 28px', borderLeft: `6px solid ${C.green}`, background: '#f5f7f5', boxSizing: 'border-box'}}>
        <Pic src="sobaya_front.png" width={161} height={215} />
        <div>
          <div style={{fontSize: 32, fontWeight: 750, lineHeight: 1.7}}>この制作手順を参考に、<br />このキャラクターを3Dにして</div>
          <div style={{fontSize: 27, color: C.green, marginTop: 18}}>回転動画は縦長・1080pで</div>
        </div>
      </div>
    </div>
  </Stage>;
}

function Setup() {
  return <Stage title="WanとTripoを、使える状態に">
    <div style={{display: 'flex', gap: 34}}>{[
      {logo: 'wan_logo.png', width: 176, height: 70},
      {logo: 'tripo_logo.svg', width: 205, height: 51},
    ].map(service => <div key={service.logo} style={{width: 453, padding: '26px 26px 29px', boxSizing: 'border-box', background: '#f5f7f5'}}>
      <div style={{height: 91, ...centre}}><Pic src={`webrefs_v3/${service.logo}`} width={service.width} height={service.height} /></div>
      <div style={{marginTop: 21, background: C.light, padding: '20px 16px', textAlign: 'center', fontSize: 29, fontWeight: 750, lineHeight: 1.65}}>
        APIキー<br />支払い設定
      </div>
    </div>)}</div>
  </Stage>;
}

export function VisualV5(props: Props) {
  if (props.view === 'codex_request') return <DelegatedWorkflow t={props.t} />;
  if (props.view === 'repo_request') return <RepositoryRequest />;
  if (props.view === 'setup') return <Setup />;
  return <VisualV4 {...props} />;
}
