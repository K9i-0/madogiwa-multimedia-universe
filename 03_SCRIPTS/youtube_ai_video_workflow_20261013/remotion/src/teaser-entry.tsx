import React from 'react';
import {AbsoluteFill, Composition, Img, interpolate, registerRoot, staticFile, useCurrentFrame} from 'remotion';
const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const opacity = interpolate(f, [0, 10, 86, 104], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: '#fff', fontFamily: '"Noto Sans JP", sans-serif', color: '#172B46'}}>
    <AbsoluteFill style={{opacity}}>
      <Img src={staticFile('expressions/yametaro_happy_closed.png')} style={{position: 'absolute', width: 245, bottom: 0, left: 20, transform: 'scaleX(-1)'}} />
      <Img src={staticFile('expressions/takosan_happy_closed.png')} style={{position: 'absolute', width: 260, bottom: 0, right: 20}} />
      <div style={{position: 'absolute', top: 200, left: 270, right: 270, textAlign: 'center'}}>
        <div style={{fontSize: 29, fontWeight: 700, marginBottom: 30}}>いつものAIで、動画づくり。</div>
        <div style={{fontSize: 66, fontWeight: 900, whiteSpace: 'nowrap', color: '#174E9F', borderBottom: '8px solid #FFD447', paddingBottom: 16}}>続きはYouTube</div>
        <div style={{fontSize: 26, marginTop: 29}}>作り方・費用・失敗の直し方を本編で</div>
      </div>
    </AbsoluteFill>
  </AbsoluteFill>;
};
registerRoot(() => <Composition id="TeaserEndCard" component={EndCard} width={1280} height={720} fps={30} durationInFrames={105}/>);
