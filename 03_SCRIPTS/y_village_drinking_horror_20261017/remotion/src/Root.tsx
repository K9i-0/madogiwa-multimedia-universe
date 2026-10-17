import React from 'react';
import {AbsoluteFill, Audio, Composition, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import edit from './edit-manifest.json';
import {WorkInsert} from './WorkInsert';
import {memberColors} from '../../../00_TEMPLATES/subtitles/member-colors';
const clamp = {extrapolateLeft:'clamp', extrapolateRight:'clamp'} as const;
const art = (name:string) => staticFile(`art/${name}.png`);
const Film:React.FC = () => {
 const f = useCurrentFrame();
 const shot = edit.shots.find(s => f >= s.from && f < s.to) ?? edit.shots[0];
 const cap = edit.captions.find(c => f >= c.from && f < c.to);
 const p = (f-shot.from)/(shot.to-shot.from);
 const ending = interpolate(f,[edit.composition.durationInFrames-90,edit.composition.durationInFrames-1],[0,1],clamp);
 const insert = edit.inserts.find(i => f >= i.from && f < i.to);
 const silhouette = !insert && shot.person && shot.person !== 'note';
 const entity = ['reveal','asleep','sobaya_clap_v6','sobaya_mug_v6','sobaya_moonlit_v7'].includes(shot.background);
 const humanHand = ['hand_can_sealed_v6','hand_can_open_v6','home_toast_v6'].includes(shot.background);
 const scale = shot.zoom + p * shot.move;
 const record = shot.view === 'recording';
 const memory = shot.view === 'memory';
 // The image appears after the line and its pause, with no flash or zoom sting.
 const titleOpacity = interpolate(f,[0,18,65,89],[0,1,1,0],clamp);
 return <AbsoluteFill style={{background:'#08090a',fontFamily:'Hiragino Mincho ProN, serif'}}>
  <Img src={art(shot.background)} style={{position:'absolute',width:'100%',height:'100%',objectFit:'cover',transformOrigin:`${shot.focusX}% ${shot.focusY}%`,transform:`scale(${scale})`,filter:`saturate(${shot.background==='f_hakama'?.8:shot.background==='sobaya_moonlit_v7'?.65:humanHand?.5:entity?.38:shot.background==='morning'?.40:.16}) brightness(${shot.brightness})`}}/>
  {silhouette && <AbsoluteFill style={{background:shot.person==='sobaya_shadow_v4'?'linear-gradient(90deg,#9c9d9666,#77786b11)':'linear-gradient(90deg,rgba(200,200,192,.58),rgba(185,185,178,.12) 80%)'}}/>}
  {silhouette && shot.person === 'duo' && <>
   <Img src={art('m_photo')} style={{position:'absolute',height:450,left:185,bottom:130}}/>
   <Img src={art('y_guitar')} style={{position:'absolute',height:520,right:245,bottom:120}}/>
  </>}
  {silhouette && shot.person !== 'duo' && <Img src={art(shot.person!)} style={{position:'absolute',height:shot.person==='f_photo'?430:shot.person==='sobaya_shadow_v4'?600:510,left:shot.person==='sobaya_shadow_v4'?380:190,bottom:shot.person==='sobaya_shadow_v4'?40:125,objectFit:'contain',opacity:shot.person==='sobaya_shadow_v4'?.77:1}}/>}
  {shot.person === 'note' && <div style={{position:'absolute',left:220,top:165,width:840,height:250,display:'flex',alignItems:'center',justifyContent:'center',background:'#c6bca3',color:'#29251f',boxShadow:'0 10px 60px #000',fontSize:38,letterSpacing:4}}>客の杯を、欠かさないこと。</div>}
  <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 38%,transparent 38%,rgba(0,0,0,.45) 100%)'}}/>
  {record && <div style={{position:'absolute',left:70,right:70,top:46,bottom:190,border:'1px solid #d4d2c452',boxShadow:'inset 0 0 80px #0003'}}>
   <div style={{position:'absolute',left:22,top:18,color:'#d7d2c8',fontSize:18,fontFamily:'monospace'}}>● REC</div>
  </div>}
  {memory && <div style={{position:'absolute',top:48,left:78,color:'#d9d4ca',fontSize:18,letterSpacing:3,opacity:.65}}>あの夜の録画</div>}
  {insert && <WorkInsert item={insert} frame={f}/>}
  <AbsoluteFill style={{background:'linear-gradient(transparent 60%,rgba(0,0,0,.74) 82%,#050606 100%)'}}/>
  {f<90 && <div style={{position:'absolute',top:250,width:'100%',textAlign:'center',color:'#eee9dd',fontSize:46,letterSpacing:12,opacity:titleOpacity}}>廃村Y村の怪異S</div>}
  {cap && <div style={{position:'absolute',left:90,right:90,bottom:60,minHeight:96,display:'flex',justifyContent:'center',alignItems:'center',textAlign:'center',whiteSpace:'pre-line',fontFamily:'Hiragino Kaku Gothic ProN, sans-serif',fontSize:32,lineHeight:1.5,fontWeight:500,letterSpacing:.3,color:'#f2f0e9',WebkitTextStroke:cap.speaker==='sobaya'?`2px ${memberColors.sobaya}`:'0px',paintOrder:'stroke fill',textShadow:'0 2px 4px #000, 0 0 10px #000',opacity:interpolate(f,[cap.from,cap.from+4],[.35,1],clamp)}}>{cap.text}</div>}
  <AbsoluteFill style={{background:'#000',opacity:ending}}/>
  <Audio src={staticFile(edit.audio)}/>
 </AbsoluteFill>;
};
export const Root:React.FC = () => <Composition id="YVillage" component={Film} width={1280} height={720} fps={30} durationInFrames={edit.composition.durationInFrames}/>;
