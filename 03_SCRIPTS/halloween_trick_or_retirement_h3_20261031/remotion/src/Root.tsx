import React from 'react';
import {AbsoluteFill,Composition,Sequence,OffthreadVideo,staticFile,useCurrentFrame,interpolate} from 'remotion';
import m from './edit-manifest.json';
import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
type Caption={startFrame:number;endFrame:number;speaker:string;text:string};
const Halloween:React.FC=()=>{
 const f=useCurrentFrame();
 const fade=interpolate(f,[m.composition.durationInFrames-12,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{backgroundColor:'#000'}}>
 {m.segments.map(s=><Sequence key={s.id} from={s.startFrame} durationInFrames={s.durationInFrames}>
 <AbsoluteFill style={{overflow:'hidden'}}><OffthreadVideo muted src={staticFile(s.file)} startFrom={s.trimStartFrame} style={{position:'absolute',width:864*1280/s.crop[2],height:480*720/s.crop[3],left:-s.crop[0]*1280/s.crop[2],top:-s.crop[1]*720/s.crop[3],maxWidth:'none'}}/></AbsoluteFill>
 </Sequence>)}
 {(m.captions as Caption[]).filter(c=>f>=c.startFrame&&f<c.endFrame).map(c=><div key={c.startFrame} style={{position:'absolute',bottom:30,left:55,right:55,textAlign:'center',fontFamily:'Hiragino Kaku Gothic ProN, sans-serif',fontSize:36,fontWeight:700,lineHeight:1.4,whiteSpace:'pre-line',...memberCaptionStyle(c.speaker)}}><span style={{display:'block',fontSize:23,marginBottom:6}}>{c.speaker}</span>{c.text}</div>)}
 <AbsoluteFill style={{backgroundColor:'#000',opacity:fade}}/>
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="Halloween" component={Halloween} width={1280} height={720} fps={24} durationInFrames={m.composition.durationInFrames}/>;
