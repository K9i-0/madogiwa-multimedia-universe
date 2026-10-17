import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,interpolate,staticFile,useCurrentFrame} from 'remotion';
import edit from './edit-manifest.json';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const art=(name:string)=>staticFile(`art/${name}.png`);
const Film:React.FC=()=>{
 const f=useCurrentFrame();
 const shot=edit.shots.find(s=>f>=s.from&&f<s.to)??edit.shots[0];
 const cap=edit.captions.find(c=>f>=c.from&&f<c.to);
 const p=(f-shot.from)/(shot.to-shot.from);
 const ending=interpolate(f,[edit.composition.durationInFrames-120,edit.composition.durationInFrames-1],[0,1],clamp);
 const silhouette=shot.person&&shot.person!=='note';
 const exactReveal=shot.background==='reveal'||shot.background==='asleep';
 const scale=1.02+p*.045;
 return <AbsoluteFill style={{background:'#08090a',fontFamily:'Hiragino Mincho ProN, serif'}}>
  <Img src={art(shot.background)} style={{position:'absolute',width:'100%',height:'100%',objectFit:'cover',transform:`scale(${scale}) translateX(${(p-.5)*(shot.crop-1)*14}px)`,filter:`saturate(${shot.background==='f_hakama'?.8:exactReveal?.62:.18}) brightness(${shot.background==='f_hakama'?.95:silhouette?.8:exactReveal?.75:.64})`}}/>
  {silhouette&&<AbsoluteFill style={{background:'linear-gradient(90deg,rgba(200,200,192,.64),rgba(185,185,178,.18) 80%)'}}/>}
  {silhouette&&shot.person==='duo'&&<><Img src={art('m_photo')} style={{position:'absolute',height:450,left:185,bottom:130}}/><Img src={art('y_guitar')} style={{position:'absolute',height:520,right:245,bottom:120}}/></>}
  {silhouette&&shot.person!=='duo'&&<Img src={art(shot.person!)} style={{position:'absolute',height:shot.person==='f_photo'?430:shot.person==='sobaya_shadow_v4'?600:510,left:shot.person==='sobaya_shadow_v4'?380:190,bottom:shot.person==='sobaya_shadow_v4'?40:125,objectFit:'contain',opacity:shot.person==='sobaya_shadow_v4'?.77:1}}/>}
  {shot.person==='note'&&<div style={{position:'absolute',left:220,top:165,width:840,height:250,display:'flex',alignItems:'center',justifyContent:'center',background:'#c6bca3',color:'#29251f',boxShadow:'0 10px 60px #000',fontSize:38,letterSpacing:4}}>客の杯を、欠かさないこと。</div>}
  <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 38%,transparent 35%,rgba(0,0,0,.45) 100%)'}}/>
  <AbsoluteFill style={{background:'linear-gradient(transparent 57%,rgba(0,0,0,.8) 80%,#050606 100%)'}}/>
  {f<90&&<div style={{position:'absolute',top:250,width:'100%',textAlign:'center',color:'#eee9dd',fontSize:46,letterSpacing:12,opacity:interpolate(f,[0,18,65,89],[0,1,1,0],clamp)}}>廃村Y村の怪異S</div>}
  {cap&&<div style={{position:'absolute',left:90,right:90,bottom:60,minHeight:96,display:'flex',justifyContent:'center',alignItems:'center',textAlign:'center',whiteSpace:'pre-line',fontFamily:'Hiragino Kaku Gothic ProN, sans-serif',fontSize:32,lineHeight:1.5,fontWeight:500,letterSpacing:.3,color:'#f2f0e9',WebkitTextStroke:('speaker' in cap && cap.speaker==='sobaya')?'2px #D93646':'0px',paintOrder:'stroke fill',textShadow:'0 2px 4px #000, 0 0 10px #000',opacity:interpolate(f,[cap.from,cap.from+3],[.4,1],clamp)}}>{cap.text}</div>}
  <AbsoluteFill style={{background:'#000',opacity:ending}}/>
  <Audio src={staticFile(edit.audio)}/>
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="YVillage" component={Film} width={1280} height={720} fps={30} durationInFrames={edit.composition.durationInFrames}/>;
