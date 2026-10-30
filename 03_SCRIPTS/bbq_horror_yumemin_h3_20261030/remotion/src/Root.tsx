import React from 'react';
import {AbsoluteFill,Composition,Sequence,OffthreadVideo,staticFile,useCurrentFrame,interpolate} from 'remotion';
import m from './edit-manifest.json';
import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
type Caption={startFrame:number;endFrame:number;speaker:string;text:string};
const captions=m.captions as Caption[];
type Segment={id:string;file:string;startFrame:number;durationInFrames:number;trimStartFrame:number;crop?:{x:number;y:number;width:number;height:number}};
const segments=m.segments as Segment[];
const BBQ:React.FC=()=>{
 const f=useCurrentFrame();
 const opacity=interpolate(f,[m.composition.durationInFrames-12,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{backgroundColor:'#000'}}>
  {segments.map(s=><Sequence key={s.id} from={s.startFrame} durationInFrames={s.durationInFrames} style={{overflow:'hidden'}}>
    <OffthreadVideo muted src={staticFile(s.file)} startFrom={s.trimStartFrame} style={s.crop?{position:'absolute',width:864*1280/s.crop.width,height:480*720/s.crop.height,left:-s.crop.x*1280/s.crop.width,top:-s.crop.y*720/s.crop.height}:{width:'100%',height:'100%',objectFit:'contain'}} />
  </Sequence>)}
  {captions.filter(c=>f>=c.startFrame&&f<c.endFrame).map(c=><div key={c.startFrame} style={{position:'absolute',bottom:38,left:35,right:35,textAlign:'center',fontFamily:'Hiragino Kaku Gothic ProN, sans-serif',fontSize:37,fontWeight:800,lineHeight:1.35,whiteSpace:'pre-line',...memberCaptionStyle(c.speaker)}}>{c.text}</div>)}
  <AbsoluteFill style={{backgroundColor:'#000',opacity}}/>
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="BBQ" component={BBQ} width={1280} height={720} fps={24} durationInFrames={m.composition.durationInFrames}/>;
