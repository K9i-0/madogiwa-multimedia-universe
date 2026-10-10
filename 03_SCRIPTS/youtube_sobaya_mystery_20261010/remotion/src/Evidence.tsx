import React from 'react';
import {Img,Loop,OffthreadVideo,Sequence,staticFile,useCurrentFrame} from 'remotion';
const durations:Record<string,number>={witness:210,gate:210,ritual:210,amber:180,ruins:60,hologram:150,awakening:120,orbital:180,gift:120};
export const Evidence:React.FC<{name:string;start:number;handheld?:boolean;still?:boolean;zoom?:number}>=({name,start,handheld=false,still=false,zoom=1})=>{
 const f=useCurrentFrame();const t=Math.max(0,f-start);const dropped=Math.floor(t/3)*3;
 const dx=handheld?Math.sin(dropped*.23)*16+Math.sin(dropped*.79)*7:Math.sin(t*.07)*.7;
 const dy=handheld?Math.cos(dropped*.19)*11+Math.sin(dropped*.51)*5:0;
 const rotation=handheld?Math.sin(dropped*.17)*1.7:0;
 const stamp=`00:${String(Math.floor((t/30)%3600/60)).padStart(2,'0')}:${String(Math.floor(t/30)%60).padStart(2,'0')}`;
 return <div style={{width:780,height:360,background:'#050a08',position:'relative',overflow:'hidden',border:'1px solid #73887955'}}>
 <div style={{position:'absolute',inset:-26,transform:`translate(${dx}px,${dy}px) rotate(${rotation}deg) scale(${zoom*1.09})`,filter:'sepia(.6) hue-rotate(65deg) brightness(.67) contrast(1.25)',opacity:t%191<2?.2:.86}}>
 {still?<Img src={staticFile(`evidence_${name}.jpg`)} style={{width:'100%',height:'100%',objectFit:'cover',imageRendering:zoom>1?'pixelated':undefined}}/>:<Sequence from={start} layout="none"><Loop durationInFrames={durations[name]} layout="none"><OffthreadVideo muted src={staticFile(`evidence_${name}.mp4`)} style={{width:'100%',height:'100%',objectFit:'cover'}}/></Loop></Sequence>}
 </div>
 <div style={{position:'absolute',inset:0,background:'repeating-linear-gradient(0deg,transparent 0px,transparent 2px,#02070499 3px,#02070499 4px)',opacity:.55}}/>
 <div style={{position:'absolute',left:0,right:0,top:(t*2.7)%420-45,height:28,background:'linear-gradient(transparent,#d4e6d01c,transparent)'}}/>
 <svg style={{position:'absolute',inset:0,width:'100%',height:'100%',opacity:.12,mixBlendMode:'screen'}}><filter id={`grain-${name}`}><feTurbulence type="fractalNoise" baseFrequency=".77" numOctaves="1" seed={Math.floor(t/6)%17}/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter={`url(#grain-${name})`}/></svg>
 {handheld&&<><div style={{position:'absolute',left:-30,top:-15,width:92,height:470,background:'#030805',transform:'rotate(13deg)',opacity:.86}}/><div style={{position:'absolute',right:-40,top:-50,width:150,height:110,background:'#030805',transform:'rotate(-25deg)',opacity:.92}}/></>}
 <div style={{position:'absolute',inset:0,boxShadow:'inset 0 0 95px 28px #000b'}}/>
 <div style={{position:'absolute',left:20,top:14,fontFamily:'monospace',fontSize:16,letterSpacing:2,color:'#c3d4b8',opacity:.8}}>{handheld?'REC / WITNESS':'CAM / FIXED OBS.'}</div>
 <div style={{position:'absolute',right:20,top:14,fontFamily:'monospace',fontSize:16,color:'#c3d4b8',opacity:.8}}>{stamp}</div>
 <div style={{position:'absolute',left:20,bottom:13,fontSize:14,letterSpacing:3,color:'#b2bea8'}}>受領記録　／　反復解析</div>
 </div>;
};
