import React from 'react';
import {AbsoluteFill,Audio,Img,staticFile,useCurrentFrame,interpolate} from 'remotion';
import m from './edit-manifest.json';
import {Panel} from './Panel';
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);const idx=m.dialogue.reduce((found,d,i)=>f>=d.startFrame?i:found,-1);const previous=m.dialogue[Math.max(idx,0)];const view=previous.view;
 let first=Math.max(idx,0);while(first>0&&m.dialogue[first-1].view===view)first--;const start=m.dialogue[first].startFrame;const elapsed=Math.max(0,f-start);const credits=f>=m.creditsStartFrame;
 const openingSilence=idx===2&&!active;
 return <AbsoluteFill style={{background:'#0b1118',fontFamily:'"Hiragino Sans",sans-serif',color:'#e6e5df'}}>
 <Audio src={staticFile('mixed.wav')}/>
 <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 30%, #23303988 0%, #091018 78%)'}}/>
 {view==='title'&&<AbsoluteFill style={{opacity:.13}}><Img src={staticFile('forest.png')} style={{width:'100%',height:'100%',objectFit:'cover'}}/></AbsoluteFill>}
 {!credits&&<>
 <div style={{position:'absolute',left:240,top:38,width:800,height:500,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',textAlign:'center',opacity:openingSilence?interpolate(f-(previous.startFrame+previous.durationInFrames),[55,95],[1,.15],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}):1}}><Panel view={view} elapsed={elapsed} start={start}/></div>
 {(['zunda','metan'] as const).map((who,i)=>{const speaking=active?.who===who;const j=active?f-active.startFrame:0;const open=speaking&&(active?.envelope[j]??0)>.025;const blink=(f+(i?49:0))%137<4;const surprise=speaking&&who==='zunda'&&/最悪|卑しい|出来悪い|社員だった|まとめて|信用できない/.test(active?.text??'');const mood=blink?'blink':surprise?'surprise':'normal';return <Img key={who} src={staticFile(`${who}_${mood}_${Number(open)}.png`)} style={{position:'absolute',left:i?1050:0,bottom:52,width:230,transform:who==='zunda'?'scaleX(-1)':undefined,filter:speaking?'none':'brightness(.86)'}}/>;})}
 {active&&<div style={{position:'absolute',left:52,right:52,bottom:28,minHeight:111,background:'#091018ef',borderTop:`1px solid ${active.who==='zunda'?'#9bbd7955':'#d6a1cc55'}`,display:'flex',alignItems:'center',justifyContent:'center',padding:'8px 12px'}}><div style={{fontSize:28,fontWeight:500,lineHeight:1.65,textAlign:'center',whiteSpace:'pre-line',color:active.who==='zunda'?'#cae6ab':'#f0c9e7'}}>{active.caption}</div></div>}
 </>}
 {credits&&<AbsoluteFill style={{alignItems:'center',justifyContent:'center',textAlign:'center',opacity:interpolate(f,[m.composition.durationInFrames-45,m.composition.durationInFrames],[1,0],{extrapolateLeft:'clamp'})}}><div style={{fontSize:32,fontFamily:'serif',marginBottom:35}}>めたんのミステリー研究所</div><div style={{fontSize:22,lineHeight:2}}>音声：VOICEVOX:四国めたん ／ VOICEVOX:ずんだもん<br/>立ち絵：坂本アヒル<br/>原作・資料映像：窓際族物語<br/>音楽：都市伝説 ／ shimtone ・ Truth Seeker ／ 松浦洋介<br/>ED：TheFatRat - Unity</div><div style={{fontSize:17,color:'#a4afb8',lineHeight:1.8,marginTop:30}}>本番組はフィクションです。研究者・報道機関・研究史は架空です。<br/>証拠映像は既存作品の再編集、復元図・解析再現図はAI生成です。<br/>参考：Oxford／Cambridge／National Geographic／CIA<br/>作品参照：『天空の城ラピュタ』／詳細は概要欄</div></AbsoluteFill>}
 </AbsoluteFill>;
};
