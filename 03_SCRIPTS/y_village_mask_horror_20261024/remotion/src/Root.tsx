import React from 'react';
import {AbsoluteFill, Audio, Composition, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import edit from './edit-manifest.json';

const clamp = {extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
type Shot=(typeof edit.shots)[number];
const art=(name:string)=>staticFile(`art/${name}.png`);
const by=Object.fromEntries(edit.narration.map(n=>[n.id,n]));
const Portrait:React.FC<{name:string;left:number;top:number;width:number;height:number}> = ({name,left,top,width,height}) => <div style={{position:'absolute',left,top,width,height,overflow:'hidden',maskImage:'linear-gradient(#000 78%,transparent 100%)'}}><Img src={art(name)} style={{width:'100%',height:'auto',display:'block'}}/></div>;

const Scene:React.FC<{shot:Shot;f:number}> = ({shot:s,f}) => {
 const p=Math.max(0,Math.min(1,(f-s.from)/(s.to-s.from)));
 let brightness=s.brightness,blur=0,opacity=1,rotate=0;
 if(s.mode==='eyes-closed'){
  brightness*=interpolate(f-s.from,[0,70,Math.max(71,s.to-s.from-1)],[.40,.17,.12],clamp);blur=7;
 }
 if(s.mode==='dawn'){
  brightness*=interpolate(p,[0,.45,1],[.05,.25,.68],clamp);blur=interpolate(p,[0,1],[18,4]);
 }
 if(s.mode==='false-voice'){
  brightness*=interpolate(f,[by.n094.to,by.n095.from,by.n096.from],[1,.55,.7],clamp);
 }
 if(s.mode==='turn')rotate=interpolate(p,[0,.66,1],[0,-1.4,-1.4]);
 if(s.fade)opacity=interpolate(f-s.from,[0,s.fade],[0,1],clamp);
 const scale=s.zoom+p*s.move+(s.mode==='turn'?.03:0);
 return <AbsoluteFill style={{opacity,overflow:'hidden'}}>
  <Img src={art(s.image)} style={{position:'absolute',width:'100%',height:'100%',objectFit:'cover',transformOrigin:`${s.focusX}% ${s.focusY}%`,transform:`scale(${scale}) rotate(${rotate}deg)`,filter:`saturate(.72) brightness(${brightness})${blur?` blur(${blur}px)`:''}`}}/>
  {s.person && <AbsoluteFill style={{background:'linear-gradient(90deg,rgba(180,176,161,.16),transparent 70%)'}}/>}
  {s.person==='duo' && <>
   <Portrait name="m_photo" left={320} top={170} width={230} height={365}/>
   <Portrait name="y_photo" left={670} top={165} width={285} height={370}/>
   <div style={{position:'absolute',left:385,top:118,color:'#d8d5cc',fontSize:20,letterSpacing:2}}>Mさん</div>
   <div style={{position:'absolute',left:735,top:118,color:'#d8d5cc',fontSize:20,letterSpacing:2}}>Yさん</div>
  </>}
  {s.person && s.person!=='duo' && <>
   <Portrait name={s.person} left={s.person==='f_photo'?225:255} top={s.person==='f_photo'?140:155} width={s.person==='f_photo'?325:s.person==='m_photo'?235:305} height={s.person==='f_photo'?420:390}/>
   <div style={{position:'absolute',left:85,top:64,color:'#e2ddd2',fontSize:18,letterSpacing:3,textShadow:'0 1px 5px #000,0 0 8px #000'}}>{s.person==='f_photo'?'F先生':s.person==='m_photo'?'Mさん':'Yさん'}</div>
  </>}
 </AbsoluteFill>;
};

const Film:React.FC=()=>{
 const f=useCurrentFrame();
 const s=edit.shots.find(s=>f>=s.from&&f<s.to)!;
 const cap=edit.captions.find(c=>f>=c.from&&f<c.to);
 const duration=edit.composition.durationInFrames;
 const opening=interpolate(f,[0,26],[1,0],clamp);
 const ending=interpolate(f,[duration-105,duration-24],[0,1],clamp);
 const special=cap?.speaker==='sobaya';
 const titleOpacity=interpolate(f,[12,35,82,108],[0,1,1,0],clamp);
 // A single dark cut follows the ceramic impact; no white flash/strobe.
 const impact=by.n021.from+45;
 const blink=f>=impact&&f<impact+7?1:0;
 return <AbsoluteFill style={{background:'#030405',fontFamily:'Hiragino Kaku Gothic ProN, sans-serif',fontSynthesis:'none',WebkitFontSmoothing:'antialiased'}}>
  <Scene shot={s} f={f}/>
  <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 40%,transparent 34%,rgba(0,0,0,.35) 100%)'}}/>
  <AbsoluteFill style={{background:'linear-gradient(transparent 58%,rgba(0,0,0,.65) 82%,rgba(0,0,0,.93) 100%)'}}/>
  {f<109&&<div style={{position:'absolute',left:60,right:60,top:255,textAlign:'center',color:'#eee9dd',fontFamily:'Hiragino Mincho ProN, serif',fontSize:48,fontWeight:500,letterSpacing:9,textShadow:'0 2px 12px #000',opacity:titleOpacity}}>廃村Y村の怪異S</div>}
  {cap&&<div data-caption-id={cap.id} style={{position:'absolute',left:85,right:85,bottom:58,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',whiteSpace:'pre-line',fontFamily:special?'Hiragino Mincho ProN, serif':undefined,fontSize:special?36:32,lineHeight:1.55,fontWeight:500,letterSpacing:special?3:.4,color:special?'#d2cec1':'#f0eee7',textShadow:'0 2px 5px #000,0 0 9px #000',opacity:interpolate(f-cap.from,[0,4],[.45,1],clamp)}}>{cap.text}</div>}
  <AbsoluteFill style={{background:'#030405',opacity:Math.max(opening,ending,blink)}}/>
  <Audio src={staticFile(edit.audio)}/>
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="YVillageMask" component={Film} width={1280} height={720} fps={30} durationInFrames={edit.composition.durationInFrames}/>;
