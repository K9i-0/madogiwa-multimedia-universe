import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
import React from 'react';
import {AbsoluteFill,Composition,OffthreadVideo,Img,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import raw from './shorts-manifest.json';
type Manifest={composition:{id:string;width:number;height:number;fps:number;durationInFrames:number};titleLines:string[];accent:string;fit:string;inputVideo:string;endcardFrom:number|null;endcardSource:string|null;captions:{startFrame:number;endFrame:number;text:string;speaker?:string}[];popup:{startFrame:number;endFrame:number;image:string}|null};
const m=raw as Manifest;
const Film:React.FC=()=>{
 const f=useCurrentFrame();const c=m.captions.find(c=>f>=c.startFrame&&f<c.endFrame);
 const end=m.endcardFrom!==null&&f>=m.endcardFrom;
 const src=staticFile(end&&m.endcardSource?m.endcardSource:m.inputVideo);
 return <AbsoluteFill style={{background:'#111820',color:'#fff',fontFamily:'"Hiragino Sans",sans-serif',fontWeight:700,overflow:'hidden'}}>
 <AbsoluteFill style={{filter:'blur(34px)',transform:'scale(1.13)',opacity:.47}}><OffthreadVideo src={src} muted style={{width:'100%',height:'100%',objectFit:'cover'}}/></AbsoluteFill>
 <AbsoluteFill style={{background:'linear-gradient(180deg,rgba(8,13,19,.7),rgba(8,13,19,.08) 48%,rgba(8,13,19,.75))'}}/>
 <div style={{position:'absolute',top:92,height:220,left:32,right:32,display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',textAlign:'center',textShadow:'0 4px 12px #0008'}}>
 <div style={{fontSize:30,letterSpacing:2,color:'#ffffff',marginBottom:20}}>{m.titleLines[0]}</div>
 <div style={{fontSize:m.titleLines[1].length>10?46:62,lineHeight:1.22,letterSpacing:-1,color:m.accent==='#ffdc86'?'#fff2d4':m.accent}}>{m.titleLines[1]}</div></div>
 <div style={{position:'absolute',top:350,left:0,width:720,height:480,overflow:'hidden'}}><OffthreadVideo src={src} muted style={{width:'100%',height:'100%',objectFit:m.fit as 'cover'|'contain'}}/></div>
 {m.popup&&f>=m.popup.startFrame&&f<m.popup.endFrame?<div style={{position:'absolute',top:871,left:60,right:90,textAlign:'center'}}><Img src={staticFile(m.popup.image)} style={{width:510,height:170,objectFit:'contain'}}/></div>:c&&<div style={{position:'absolute',top:876,left:40,right:88,textAlign:'center'}}>
 {c.speaker&&<div style={{display:'inline-block',fontSize:28,fontWeight:700,color:'#ffffff',padding:'2px 0',marginBottom:12,letterSpacing:1,textShadow:'0 2px 5px #0009'}}>{c.speaker}</div>}
 <div style={{fontSize:38,lineHeight:1.5,whiteSpace:'pre-line',...memberCaptionStyle(c.speaker)}}>{c.text}</div></div>}
 </AbsoluteFill>;
};
registerRoot(()=> <Composition {...m.composition} component={Film}/>);
