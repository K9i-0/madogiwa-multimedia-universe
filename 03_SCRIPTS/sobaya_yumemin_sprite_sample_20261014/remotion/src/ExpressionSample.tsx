import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import data from './manifest_expressions.json';
import {memberCaptionStyle} from './member-colors';
type Rect=[number,number,number,number];
const faces:Record<string,{width:number;height:number;mouth:Rect}>={
 normal:{width:1164,height:1351,mouth:[477,300,64,63]},
 beer_cheers:{width:1024,height:1536,mouth:[457,402,69,54]},
};
const clip=(r:Rect,w:number,h:number)=>`inset(${r[1]/h*100}% ${(w-r[0]-r[2])/w*100}% ${(h-r[1]-r[3])/h*100}% ${r[0]/w*100}%)`;
export function mouthOpenAt(frame:number){
 const line=data.lines.find(l=>frame>=l.start&&frame<l.start+l.frames);
 if(!line||line.who!=='sobaya')return false;
 const local=frame-line.start;
 const env=(line.energy[local]??0)*.6+(line.energy[Math.max(0,local-1)]??0)*.25+(line.energy[Math.max(0,local-2)]??0)*.15;
 return env>.09 && Math.floor(local/3)%3!==2;
}
export const ExpressionSample:React.FC=()=>{
 const f=useCurrentFrame();
 const line=data.lines.find(l=>f>=l.start&&f<l.start+l.frames+12);
 const last=[...data.lines].reverse().find(l=>f>=l.start);
 const pose=last?.pose??'normal';const expression=last?.yumeminExpression??'happy';
 const local=line?f-line.start:0;const speaking=!!line&&local<line.frames;
 const energy=speaking?(line.energy[local]??0):0;
 const cfg=faces[pose];const open=mouthOpenAt(f);
 const sw=cfg?.width??1164,sh=cfg?.height??1351;
 const height=484,width=height*sw/sh,left=(485-width)/2;
 const fade=interpolate(f,[0,10,data.composition.durationInFrames-15,data.composition.durationInFrames-1],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 const ymove=Math.sin(f/23)*1.8-(speaking&&line?.who==='yumemin'?energy*2.5:0);
 return <AbsoluteFill style={{background:'#fff',fontFamily:'Hiragino Sans, sans-serif'}}><AbsoluteFill style={{opacity:fade}}>
 <div style={{position:'absolute',left:70,top:38,color:'#667078',fontSize:22,letterSpacing:2}}>そば屋 × ゆめみん</div>
 <div style={{position:'absolute',right:70,top:42,color:'#889096',fontSize:16}}>表情・口パク サンプル</div>
 <div style={{position:'absolute',left:84,top:83,width:485,height:484,transform:'scaleX(-1)'}}>
 <div style={{position:'absolute',left,top:0,width,height}}>
 <Img src={staticFile(`sobaya_v2/sobaya_${pose}.png`)} style={{position:'absolute',width,height}}/>
 {cfg&&open&&<Img src={staticFile(`sobaya_v2/sobaya_${pose}_talk.png`)} style={{position:'absolute',width,height,clipPath:clip(cfg.mouth,sw,sh)}}/>}
 </div></div>
 <div style={{position:'absolute',right:110,top:214,width:360,height:340,transform:`translateY(${ymove}px)`}}>
 <Img src={staticFile(`yumemin_${expression}.png`)} style={{width:'100%',height:'100%',objectFit:'contain'}}/>
 </div>
 <div style={{position:'absolute',left:0,right:0,top:592,textAlign:'center',padding:'0 60px',fontSize:34,fontWeight:700,lineHeight:1.45,...memberCaptionStyle(line?.who==='sobaya'?'そば屋':'ゆめみん')}}>{line?.text??''}</div>
 </AbsoluteFill>{data.lines.map(l=><Sequence key={l.audio} from={l.start} durationInFrames={l.frames}><Audio src={staticFile(l.audio)}/></Sequence>)}</AbsoluteFill>;
};
