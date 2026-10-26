import React from 'react';
import {AbsoluteFill,Audio,OffthreadVideo,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
import manifest from './edit-manifest-h3.json';
export function H3Film(){
 const frame=useCurrentFrame();
 const line=manifest.lines.find(l=>frame>=l.start&&frame<l.end);
 const fade=interpolate(frame,[manifest.durationInFrames-25,manifest.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{backgroundColor:'#000',fontFamily:'Hiragino Kaku Gothic ProN, sans-serif'}}>
  {manifest.shots.map(s=><Sequence key={s.id} from={s.start} durationInFrames={s.end-s.start}>
   <OffthreadVideo src={staticFile(s.video)} startFrom={s.trimStart} muted style={{width:'100%',height:'100%',objectFit:'contain'}} />
  </Sequence>)}
  <Audio src={staticFile(manifest.audio)}/>
  {line&&<div style={{position:'absolute',left:64,right:64,bottom:38,textAlign:'center',fontSize:30,fontWeight:600,lineHeight:1.45,whiteSpace:'pre-wrap'}}>
   <span style={{...memberCaptionStyle('そば屋'),display:'inline-block',padding:'5px 16px',borderRadius:4,backgroundColor:'rgba(0,0,0,.62)'}}>{line.text}</span>
  </div>}
  <AbsoluteFill style={{backgroundColor:'#000',opacity:fade}}/>
 </AbsoluteFill>;
}
