import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,OffthreadVideo,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import timings from './edit-manifest.json';
import {FinalNews, finalSpec} from './FinalNews';
import {ForestGraphic,ComparisonGraphic} from './NewsGraphics';
const navy='#183a62',white='#fcfcff';
const font='"Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif';
const Bug=()=> <><div style={{position:'absolute',top:25,left:30,background:navy,color:white,padding:'5px 18px',fontSize:32,fontWeight:700}}>{timings.final.clock}</div><div style={{position:'absolute',top:18,right:22,width:190,height:64,background:navy,color:'white',display:'flex',alignItems:'center',justifyContent:'center',fontSize:34,fontWeight:800}}>ゆめテレ</div></>;
const Band=({label,title,sub}:{label:string,title:string,sub?:string})=><div style={{position:'absolute',bottom:22,left:32,right:32,boxShadow:'0 4px 14px #0004'}}><div style={{background:navy,color:'white',display:'inline-block',padding:'7px 18px',fontSize:23,fontWeight:700}}>{label}</div><div style={{background:'#fcfdff',borderLeft:'8px solid #c58a35',padding:'13px 22px',color:navy}}><div style={{fontSize:40,fontWeight:700}}>{title}</div>{sub&&<div style={{fontSize:23,marginTop:5}}>{sub}</div>}</div></div>;
const Shot=({kind}:{kind:string})=>{const f=useCurrentFrame();return <AbsoluteFill style={{background:'#e9ecee',fontFamily:font}}>
{kind==='intro'&&<><OffthreadVideo src={staticFile('anchor_intro.mp4')} style={{width:'100%',height:'100%',objectFit:'cover'}}/><Band label="季節の話題" title="秋の味覚　ちくわ狩り最盛期"/></>}
{kind==='forest'&&<><Img src={staticFile('forest_v2.png')} style={{width:'100%',height:'100%',objectFit:'cover',transform:`scale(${interpolate(f,[0,timings.forest-1],[1,1.012],{extrapolateRight:'clamp'})})`}}/><Audio src={staticFile('voice_forest.wav')}/><ForestGraphic/></>}
{kind==='comparison'&&<><ComparisonGraphic/><Audio src={staticFile('voice_comparison.wav')}/></>}
{kind==='interruption'&&<><AbsoluteFill style={{background:'linear-gradient(125deg,#102b4c,#244867)',alignItems:'center',justifyContent:'center',color:white}}><div style={{width:700,borderTop:'2px solid #90a4ba',borderBottom:'2px solid #90a4ba',textAlign:'center',padding:'42px 0'}}><div style={{fontSize:44,fontWeight:700,letterSpacing:3}}>中継を中断しています</div><div style={{fontSize:24,marginTop:20,color:'#d7e1eb'}}>しばらくお待ちください</div></div></AbsoluteFill><Sequence from={8}><Audio src={staticFile('voice_interruption.wav')}/></Sequence></>}
{kind==='expert'&&<><Img src={staticFile('okayaman_expert_clean.png')} style={{width:'100%',height:'100%'}}/><Band label="窓際大学大学院 農学研究科　准教授" title="おかやまん" sub="専門：ちくわ生物学"/></>}
{kind!=='comparison'&&kind!=='forest'&&<Bug/>}</AbsoluteFill>};
const order=['intro','forest','comparison','interruption'] as const;
const Parts=()=>{let start=0;return <AbsoluteFill>{order.map(k=>{const at=start;start+=timings[k];return <Sequence key={k} from={at} durationInFrames={timings[k]}><Shot kind={k}/></Sequence>})}</AbsoluteFill>};
export const Root=()=> <><Composition id="FinalNews" component={FinalNews} durationInFrames={finalSpec.composition.durationInFrames} fps={30} width={1280} height={720}/>{order.map(k=><Composition key={k} id={k} component={()=> <Shot kind={k}/>} durationInFrames={timings[k]} fps={30} width={1280} height={720}/>)}<Composition id="Parts" component={Parts} durationInFrames={order.reduce((s,k)=>s+timings[k],0)} fps={30} width={1280} height={720}/><Composition id="ExpertCard" component={()=> <Shot kind="expert"/>} durationInFrames={90} fps={30} width={1280} height={720}/></>;
