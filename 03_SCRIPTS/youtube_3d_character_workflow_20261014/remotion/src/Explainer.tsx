import React from 'react';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame,interpolate} from 'remotion';
import manifest from './edit-manifest.json';
import {SpreadsheetFrame} from './SpreadsheetFrame';
import {DuoSprite,Mood} from './DuoSprite';
import {captionColors} from './theme';
import {Visual} from './Visual';
export function Explainer({audioEnabled=true}:{audioEnabled?:boolean}){
 const f=useCurrentFrame();const m=manifest;const idx=m.dialogue.reduce((last,d,i)=>f>=d.startFrame?i:last,0);const prev=m.dialogue[idx];const active=f<prev.startFrame+prev.durationInFrames&&f>=prev.startFrame?prev:null;
 let viewStart=idx;while(viewStart>0&&m.dialogue[viewStart-1].view===prev.view)viewStart--;
 const t=Math.max(0,f-m.dialogue[viewStart].startFrame)/30;
 const local=active?f-active.startFrame:0;const segments=(active as any)?.captionSegments??[];const caption=segments.find((s:any)=>local>=s.startFrame&&local<s.endFrame)?.text??'';
 return <AbsoluteFill style={{background:'#fff',fontFamily:'"Hiragino Sans",sans-serif',color:'#182F24'}}>
 {audioEnabled&&<Audio src={staticFile('mixed.wav')}/>}
 <SpreadsheetFrame chapter={prev.chapter}>
 <div style={{position:'absolute',left:245,top:110,width:790,height:440,display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',textAlign:'center',background:'#fff',fontSize:24}}><Visual view={prev.view} t={t}/></div>
 {(['yametaro','takosan'] as const).map(who=>{
 const speaking=active?.who===who;const peak=Math.max(...(active?.envelope??[0]));const open=who==='yametaro'&&speaking&&(active?.envelope[Math.floor(local/2)*2]??0)>Math.max(.003,peak*.14);
 let mood:Mood='normal';if(who==='yametaro')mood=/全然違う|八本|増える|追いかけ/.test(prev.text)?'surprise':/無料|休日|困る|なんか違|コスト/.test(prev.text)?'worry':/こっちや|やってみ|再現度|住みつく/.test(prev.text)?'happy':'normal';
 return <DuoSprite key={who} who={who} speaking={speaking} open={open} mood={mood} local={local}/>;
 })}
 {active&&<div style={{position:'absolute',left:245,right:245,bottom:42,height:112,background:'#fff',borderTop:'1px solid #cbd4ce',display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{fontSize:29,fontWeight:700,lineHeight:1.6,whiteSpace:'pre-line',textAlign:'center',color:captionColors[active.who as 'yametaro'|'takosan']}}>{caption}</div></div>}
 </SpreadsheetFrame><AbsoluteFill style={{pointerEvents:'none',background:'#fff',opacity:interpolate(f,[m.composition.durationInFrames-30,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
 </AbsoluteFill>;
}
