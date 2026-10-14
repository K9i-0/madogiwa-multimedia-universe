import React from 'react';
import {AbsoluteFill,Audio,staticFile,useCurrentFrame,interpolate} from 'remotion';
import manifest from './edit-manifest-v5.json';
import {SpreadsheetFrameV3} from './SpreadsheetFrameV3';
import {DuoSpriteV5} from './DuoSpriteV5';
import {captionColors} from './theme';
import {VisualV5} from './VisualV5';
export function ExplainerV5({audioEnabled=true}:{audioEnabled?:boolean}){
 const f=useCurrentFrame();const m=manifest;const idx=m.dialogue.reduce((last,d,i)=>f>=d.startFrame?i:last,0);const d=m.dialogue[idx];const local=Math.max(0,f-d.startFrame);const speaking=local<d.durationInFrames&&f>=d.startFrame;
 let first=idx;while(first>0&&m.dialogue[first-1].view===d.view)first--;
 const t=Math.max(0,f-m.dialogue[first].startFrame)/30;
 const segments=(d as any).captionSegments??[];const caption=segments.find((s:any)=>local>=s.startFrame&&local<s.endFrame)?.text??(f>=d.startFrame?segments.at(-1)?.text??'':'');
 const chapterRows=m.dialogue.filter(r=>r.chapter===d.chapter);const chapterStart=chapterRows[0].startFrame;const last=chapterRows[chapterRows.length-1];const chapterEnd=last.startFrame+last.durationInFrames;const progress=Math.max(0,Math.min(1,(f-chapterStart)/(chapterEnd-chapterStart)));
 return <AbsoluteFill style={{background:'#fff',fontFamily:'"Hiragino Sans",sans-serif',color:'#182F24'}}>
 {audioEnabled&&<Audio src={staticFile('mixed-v5.wav')}/>}
 <SpreadsheetFrameV3 chapter={d.chapter} progress={progress}>
 <div style={{position:'absolute',left:140,top:90,width:1000,height:470,background:'#fff'}}><VisualV5 view={d.view} t={t} text={d.text} localT={local/30} id={d.id}/></div>
 {(['yametaro','takosan'] as const).map(who=>{
  const isSpeaking=speaking&&d.who===who;const peak=Math.max(...(d.envelope??[0]));const open=who==='yametaro'&&isSpeaking&&(d.envelope[Math.floor(local/2)*2]??0)>Math.max(.003,peak*.14);
  return <DuoSpriteV5 key={who} who={who} id={d.id} speaking={isSpeaking} open={open} local={local} durationInFrames={d.durationInFrames}/>;
 })}
 {caption&&<div style={{position:'absolute',left:170,right:170,top:575,height:106,background:'#fff',borderTop:'1px solid #d9e1db',display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{fontSize:32,fontWeight:700,lineHeight:1.45,whiteSpace:'pre-line',textAlign:'center',color:captionColors[d.who as 'yametaro'|'takosan']}}>{caption}</div></div>}
 </SpreadsheetFrameV3>
 <AbsoluteFill style={{pointerEvents:'none',background:'#fff',opacity:interpolate(f,[m.composition.durationInFrames-24,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
 </AbsoluteFill>;
}
