import React from 'react';
import {AbsoluteFill, Composition, Freeze, Img, OffthreadVideo, Sequence, interpolate, registerRoot, staticFile, useCurrentFrame} from 'remotion';
import {ExplainerV6} from './ExplainerV6';
import m from './shorts-manifest.json';
import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';

const Shorts:React.FC=()=>{
 const f=useCurrentFrame();
 const c=m.captions.find(c=>f>=c.startFrame&&f<c.endFrame);
 const end=f>=m.cutFrame;
 return <AbsoluteFill style={{background:'#111c19',color:'#fff',fontFamily:'"Hiragino Sans",sans-serif',fontWeight:700}}>
  <AbsoluteFill style={{filter:'blur(34px)',opacity:.3,transform:'scale(1.13)'}}>
   <Freeze frame={Math.min(f,m.cutFrame-1)}><OffthreadVideo muted src={staticFile('shorts_source_v6.mp4')} style={{width:'100%',height:'100%',objectFit:'cover'}}/></Freeze>
  </AbsoluteFill>
  <AbsoluteFill style={{background:'linear-gradient(180deg,#071c18cc,#071c1822 48%,#071c18ee)'}}/>
  <div style={{position:'absolute',top:100,left:32,right:55,textAlign:'center',textShadow:'0 4px 12px #0008'}}>
   <div style={{fontSize:29,marginBottom:22}}>Codex × Tripo</div>
   <div style={{color:'#fff2d4'}}><div style={{fontSize:36,whiteSpace:'nowrap'}}>自分のキャラを、</div><div style={{fontSize:64,marginTop:12}}>動く3Dに。</div></div>
  </div>
  {!end ? <>
   <div style={{position:'absolute',top:368,left:0,width:720,height:405,overflow:'hidden'}}>
    <div style={{width:1280,height:720,transform:'scale(0.5625)',transformOrigin:'top left'}}><ExplainerV6 hideCaptions audioEnabled={false}/></div>
   </div>
   {c&&<div style={{position:'absolute',top:861,left:40,right:88,textAlign:'center'}}>
    <div style={{fontSize:28,marginBottom:15,textShadow:'0 2px 5px #0009'}}>{c.speaker}</div>
    <div style={{fontSize:38,lineHeight:1.5,whiteSpace:'pre-line',...memberCaptionStyle(c.speaker)}}>{c.text}</div>
   </div>}
  </> : <AbsoluteFill style={{opacity:interpolate(f,[m.cutFrame,m.cutFrame+8],[0,1],{extrapolateRight:'clamp'})}}>
   <div style={{position:'absolute',left:36,right:60,top:420,textAlign:'center'}}>
    <div style={{fontSize:29,marginBottom:28}}>作り方・費用・動かし方</div>
    <div style={{fontSize:53,lineHeight:1.5,color:'#fff2d4'}}>続きは<br/>関連動画から</div>
   </div>
   <Img src={staticFile('expressions/yametaro_happy_closed.png')} style={{position:'absolute',left:75,top:740,width:205,transform:'scaleX(-1)'}}/>
   <Img src={staticFile('expressions/takosan_happy_closed.png')} style={{position:'absolute',right:100,top:780,width:230}}/>
  </AbsoluteFill>}
  <AbsoluteFill style={{background:'#111c19',opacity:interpolate(f,[m.durationInFrames-12,m.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
 </AbsoluteFill>;
};
registerRoot(()=> <Composition id="WorkflowShorts" component={Shorts} width={720} height={1280} fps={30} durationInFrames={m.durationInFrames}/>);
