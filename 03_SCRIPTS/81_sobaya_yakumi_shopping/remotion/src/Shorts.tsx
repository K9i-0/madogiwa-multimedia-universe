import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
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
    <div aria-label={m.title} style={{position:'absolute',top:92,height:220,left:32,right:32,display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',textAlign:'center',fontWeight:700,textShadow:'0 4px 12px #0008'}}>
      <div style={{fontSize:30,letterSpacing:2,color:'#ffffff',marginBottom:20}}>そば屋の</div>
      <div style={{fontSize:62,lineHeight:1.22,letterSpacing:-1,color:'#fff2d4'}}>楽しいそば作り</div>
    </div>
    <div style={{position:'absolute',top:350,left:0,width:720,height:480,overflow:'hidden',boxShadow:'0 12px 40px #0006'}}>
      <OffthreadVideo src={src} muted style={{width:'100%',height:'100%',objectFit:'cover'}} />
    </div>
    {caption && <div style={{position:'absolute',top:876,left:40,right:88,textAlign:'center'}}>
      <div style={{display:'inline-block',fontSize:20,fontWeight:500,color:'#ffffff',padding:'6px 0',marginBottom:16,letterSpacing:1,textShadow:'0 2px 5px #0009'}}>{caption.speaker}</div>
      <div style={{fontSize:39,lineHeight:1.5,whiteSpace:'pre-line',...memberCaptionStyle(caption.speaker)}}>{caption.text.replace(/\\n/g,'\n')}</div>
    </div>}
  </AbsoluteFill>;
};
