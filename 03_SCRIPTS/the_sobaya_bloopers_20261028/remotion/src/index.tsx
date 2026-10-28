import React from 'react';
import {AbsoluteFill,Composition,OffthreadVideo,registerRoot,staticFile,useCurrentFrame,interpolate} from 'remotion';
import m from './edit-manifest.json';
import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
type Caption={startFrame:number;endFrame:number;text:string;speaker:string};
const Film:React.FC=()=>{
 const f=useCurrentFrame();
 const s=m.segments.find(s=>f>=s.start&&f<s.start+s.duration)!;
 const local=f-s.start;
 const caption=(m.captions as Caption[]).find(c=>f>=c.startFrame&&f<c.endFrame);
 const title=f<83;
 const labelOpacity=interpolate(local,[0,5,70,80],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 const fade=interpolate(f,[m.composition.durationInFrames-10,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{backgroundColor:'#101214',fontFamily:'"Hiragino Sans", sans-serif',color:'#fff',fontWeight:600}}>
  <OffthreadVideo src={staticFile('master.mp4')} muted style={{width:1280,height:720}}/>
  <div style={{position:'absolute',top:38,left:48,display:'flex',alignItems:'center',gap:12,opacity:labelOpacity}}>
   <div style={{background:s.id.startsWith('ng')?'#e23339':'#111c',padding:'8px 12px',fontSize:22,letterSpacing:2}}>{s.label}</div>
   <div style={{fontSize:23,textShadow:'0 2px 5px #000',background:'#1118',padding:'8px 12px'}}>{s.heading}</div>
  </div>
  <div style={{position:'absolute',right:48,top:43,fontSize:17,letterSpacing:3,textShadow:'0 2px 4px #000'}}>THE SOBAYA <span style={{color:'#ffcf6c'}}> / NG</span></div>
  {title&&<div style={{position:'absolute',left:48,bottom:51,textShadow:'0 3px 8px #000',opacity:interpolate(f,[0,7,66,82],[0,1,1,0],{extrapolateRight:'clamp'})}}><div style={{fontSize:46,letterSpacing:4}}>BEHIND THE CHAOS</div><div style={{fontSize:21,letterSpacing:3,marginTop:6}}>THE SOBAYA 撮影の裏側</div></div>}
  {caption&&<div style={{position:'absolute',bottom:54,left:52,right:52,textAlign:'center',whiteSpace:'pre-line',fontSize:37,lineHeight:1.35,...memberCaptionStyle(caption.speaker)}}>{caption.text}</div>}
  <AbsoluteFill style={{backgroundColor:'#000',opacity:fade}}/>
 </AbsoluteFill>
};
registerRoot(()=> <Composition id={m.composition.id} component={Film} width={1280} height={720} fps={30} durationInFrames={m.composition.durationInFrames}/>);
