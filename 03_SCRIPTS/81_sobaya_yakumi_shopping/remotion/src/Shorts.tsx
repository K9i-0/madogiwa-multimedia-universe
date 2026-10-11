import React from 'react';
import {AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import m from './shorts-manifest.json';

export const YakumiShorts: React.FC = () => {
  const frame = useCurrentFrame();
  const caption = m.captions.find(c => frame >= c.startFrame && frame < c.endFrame);
  const src = staticFile(m.inputVideo);
  return <AbsoluteFill style={{background:'#111820',color:'#fff',fontFamily:'"Hiragino Sans", "Noto Sans CJK JP", sans-serif',fontWeight:700,overflow:'hidden'}}>
    <AbsoluteFill style={{filter:'blur(34px)',transform:'scale(1.13)',opacity:.47}}>
      <OffthreadVideo src={src} muted style={{width:'100%',height:'100%',objectFit:'cover'}} />
    </AbsoluteFill>
    <AbsoluteFill style={{background:'linear-gradient(180deg,rgba(8,13,19,.7),rgba(8,13,19,.08) 48%,rgba(8,13,19,.75))'}} />
    <div style={{position:'absolute',top:190,left:40,right:40,fontSize:44,lineHeight:1.4,textAlign:'center',fontWeight:600,textShadow:'0 2px 8px #0008'}}>{m.title}</div>
    <div style={{position:'absolute',top:350,left:0,width:720,height:480,overflow:'hidden',boxShadow:'0 12px 40px #0006'}}>
      <OffthreadVideo src={src} muted style={{width:'100%',height:'100%',objectFit:'cover'}} />
    </div>
    {caption && <div style={{position:'absolute',top:876,left:40,right:88,textAlign:'center'}}>
      <div style={{fontSize:21,color:caption.speaker.includes('そば屋')?'#ffe268':'#c9dbe5',marginBottom:14,letterSpacing:1}}>{caption.speaker}</div>
      <div style={{fontSize:38,lineHeight:1.45,whiteSpace:'pre-line',textShadow:'0 2px 8px #000, 0 0 3px #000'}}>{caption.text.replace(/\\n/g,'\n')}</div>
    </div>}
  </AbsoluteFill>;
};
