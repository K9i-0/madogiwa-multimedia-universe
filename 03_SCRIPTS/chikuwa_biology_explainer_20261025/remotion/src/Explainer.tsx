import React from 'react';
import {AbsoluteFill,Img,Sequence,OffthreadVideo,staticFile,useCurrentFrame} from 'remotion';
import m from './edit-manifest.json';
import {Visual} from './Visuals';
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);const previous=[...m.dialogue].reverse().find(d=>f>=d.startFrame)??m.dialogue[0];const clip=m.clips.find(c=>f>=c.startFrame&&f<c.startFrame+c.durationInFrames);const caption=m.captions.find(c=>f>=c.startFrame&&f<c.endFrame);const start=m.views.find(v=>v.view===previous.view&&f>=v.startFrame&&f<v.endFrame)?.startFrame??previous.startFrame;
 const fade=Math.min(1,(m.composition.durationInFrames-f)/45);
 return <AbsoluteFill style={{background:'#f5f3ea',color:'#293e38',fontFamily:'"Hiragino Sans",sans-serif'}}><AbsoluteFill style={{opacity:fade}}>
 <div style={{position:'absolute',left:240,top:28,width:800,height:530,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',textAlign:'center'}}>
 {clip?<Sequence from={clip.startFrame} durationInFrames={clip.durationInFrames} layout="none"><OffthreadVideo muted src={staticFile(clip.src)} startFrom={clip.sourceStartFrame} style={{width:800,height:450,objectFit:'contain'}}/><div style={{fontSize:18,marginTop:14,color:'#657569'}}>{clip.label}</div></Sequence>:<Sequence from={start} layout="none"><Visual key={start} view={previous.view} local={f-start}/></Sequence>}
 </div>
 {(['zunda','metan'] as const).map((who,i)=>{const speak=active?.who===who;const j=active?f-active.startFrame:0;const open=speak&&(active?.envelope[j]??0)>.022;const blink=(f+(i?57:0))%143<4;return <Img key={who} src={staticFile(`${who}_${blink?'blink':'normal'}_${Number(open)}.png`)} style={{position:'absolute',left:i?1042:-2,bottom:7,width:240,transform:who==='zunda'?'scaleX(-1)':undefined}}/>})}
 {caption&&!clip&&<div style={{position:'absolute',left:82,right:82,top:581,height:108,display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{fontSize:29,fontWeight:700,lineHeight:1.6,whiteSpace:'pre-line',textAlign:'center',color:active?.who==='zunda'?'#347526':'#8d397c',WebkitTextStroke:'5px #fffdf7',paintOrder:'stroke fill',textShadow:'0 2px 3px #0002'}}>{caption.text}</div></div>}
 </AbsoluteFill></AbsoluteFill>;
};
