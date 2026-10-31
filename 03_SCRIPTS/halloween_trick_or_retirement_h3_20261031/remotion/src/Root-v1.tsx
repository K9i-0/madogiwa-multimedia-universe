import React from 'react';
import {AbsoluteFill,Composition,Sequence,OffthreadVideo,staticFile,useCurrentFrame,interpolate} from 'remotion';
import m from './edit-manifest-v1.json';
import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
type Caption={startFrame:number;endFrame:number;speaker:string;text:string};
const Halloween:React.FC=()=>{
 const f=useCurrentFrame();
 const fade=interpolate(f,[m.composition.durationInFrames-12,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{backgroundColor:'#000'}}>
 {m.segments.map(s=><Sequence key={s.id} from={s.startFrame} durationInFrames={s.durationInFrames}>
 <OffthreadVideo muted src={staticFile(s.file)} startFrom={s.trimStartFrame} style={{width:'100%',height:'100%',objectFit:'contain'}}/>
 </Sequence>)}
 {(m.captions as Caption[]).filter(c=>f>=c.startFrame&&f<c.endFrame).map(c=><div key={c.startFrame} style={{position:'absolute',bottom:42,left:55,right:55,textAlign:'center',fontFamily:'Hiragino Kaku Gothic ProN, sans-serif',fontSize:38,fontWeight:700,lineHeight:1.4,whiteSpace:'pre-line',...memberCaptionStyle(c.speaker)}}>{c.text}</div>)}
 <AbsoluteFill style={{backgroundColor:'#000',opacity:fade}}/>
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="Halloween" component={Halloween} width={1280} height={720} fps={24} durationInFrames={m.composition.durationInFrames}/>;
