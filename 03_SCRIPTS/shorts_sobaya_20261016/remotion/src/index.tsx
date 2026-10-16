import React from 'react';
import {AbsoluteFill,Composition,registerRoot,useCurrentFrame} from 'remotion';
import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
const Overlay:React.FC<any>=(m)=>{
 const f=useCurrentFrame(),c=m.captions.find((c:any)=>f>=c.startFrame&&f<c.endFrame);
 const lines=m.titleCues?.reduce((a:any,c:any)=>f>=c.from?c.titleLines:a,m.titleLines)??m.titleLines;
 const main=lines.at(-1),small=lines.length>1?lines[0]:'';
 return <AbsoluteFill style={{color:'#fff',fontFamily:'"Hiragino Sans",sans-serif',fontWeight:700,overflow:'hidden'}}>
 <AbsoluteFill style={{background:'linear-gradient(180deg,rgba(8,13,19,.7),rgba(8,13,19,.08) 48%,rgba(8,13,19,.75))'}}/>
 <div style={{position:'absolute',top:92,height:220,left:32,right:32,display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',textAlign:'center',textShadow:'0 4px 12px #0008'}}>
 {small&&<div style={{fontSize:30,letterSpacing:2,color:'#fff',marginBottom:20}}>{small}</div>}
 <div style={{fontSize:main.length>15?40:main.length>10?46:62,lineHeight:1.22,letterSpacing:-1,color:m.accent??'#fff2d4',whiteSpace:'pre-line'}}>{main}</div></div>
 {c&&<div style={{position:'absolute',top:876,left:40,right:88,textAlign:'center'}}>
 {c.speaker&&<div style={{display:'inline-block',fontSize:28,fontWeight:700,color:'#fff',padding:'2px 0',marginBottom:12,letterSpacing:1,textShadow:'0 2px 5px #0009'}}>{c.speaker}</div>}
 <div style={{fontSize:38,lineHeight:1.5,whiteSpace:'pre-line',...memberCaptionStyle(c.speaker)}}>{c.text}</div></div>}
 {m.credits?.filter((c:any)=>f>=c.from&&f<c.to).map((c:any,i:number)=><div key={i} style={{position:'absolute',top:1158,left:40,right:88,textAlign:'center',fontSize:22,fontWeight:500,color:'#fff',textShadow:'0 2px 6px #000'}}>{c.text}</div>)}
 </AbsoluteFill>;
};
registerRoot(()=> <Composition id="Overlay" component={Overlay} width={720} height={1280} fps={24} durationInFrames={24} defaultProps={{titleLines:[''],captions:[]}} calculateMetadata={({props}:any)=>({fps:props.fps,durationInFrames:props.durationInFrames})}/>);
