import {memberColor, memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
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
 <div style={{position:'absolute',top:142,left:36,right:36,textAlign:'center',textShadow:'0 3px 0 #17212b,0 8px 18px #0005'}}>
 <div style={{fontSize:32,letterSpacing:3,color:'#fff5de',marginBottom:14}}>{m.titleLines[0]}</div>
 <div style={{display:'inline-block',fontSize:m.titleLines[1].length>10?45:57,lineHeight:1.3,letterSpacing:1,color:m.accent,paddingBottom:14,borderBottom:`3px solid ${m.accent}99`}}>{m.titleLines[1]}</div></div>
 <div style={{position:'absolute',top:350,left:0,width:720,height:480,overflow:'hidden'}}><OffthreadVideo src={src} muted style={{width:'100%',height:'100%',objectFit:m.fit as 'cover'|'contain'}}/></div>
 {m.popup&&f>=m.popup.startFrame&&f<m.popup.endFrame?<div style={{position:'absolute',top:871,left:60,right:90,textAlign:'center'}}><Img src={staticFile(m.popup.image)} style={{width:510,height:170,objectFit:'contain'}}/></div>:c&&<div style={{position:'absolute',top:876,left:40,right:88,textAlign:'center'}}>
 {c.speaker&&<div style={{display:'inline-block',fontSize:20,color:memberColor(c.speaker),background:'#17212bc9',border:'1px solid #ffffff30',borderRadius:7,padding:'5px 15px',marginBottom:16,letterSpacing:1}}>{c.speaker}</div>}
 <div style={{fontSize:38,lineHeight:1.5,whiteSpace:'pre-line',...memberCaptionStyle(c.speaker)}}>{c.text}</div></div>}
 </AbsoluteFill>;
};
registerRoot(()=> <Composition {...m.composition} component={Film}/>);
