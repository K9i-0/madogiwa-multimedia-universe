import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,Sequence,interpolate,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import m from './aura-hazard-wideui.json';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const ease=(f:number,a:number,b:number,x:number,y:number)=>interpolate(f,[a,b],[x,y],clamp);
const mono='"SFMono-Regular", Menlo, monospace';
type Seg=typeof m.segments[number];
const Scanner=()=>{const f=useCurrentFrame();const danger=f>=m.scannerTiming.yameEnd;return <AbsoluteFill style={{background:'#000',justifyContent:'center'}}><div style={{position:'absolute',left:0,top:437.5,width:1280,height:720,transform:'scale(0.5625)',transformOrigin:'top left',overflow:'hidden',background:'radial-gradient(ellipse at 40% 35%,#133132,#020a0e 80%)',color:'#c6e0df'}}>
 <svg viewBox="0 0 1280 720" style={{position:'absolute',inset:0,opacity:.16}}>{Array.from({length:19},(_,i)=><path key={i} d={`M 0 ${i*70} H 1280 M ${i*70} 0 V 720`} stroke="#407d7a" strokeWidth=".5"/>)}</svg>
 <div style={{position:'absolute',left:48,right:48,top:24,display:'flex',justifyContent:'space-between',fontFamily:mono,fontSize:18,letterSpacing:2,color:'#679f9c'}}><span>TAKO LAB / 07</span><span style={{color:'#9ff2db'}}>● LIVE</span></div>
 <div style={{position:'absolute',left:48,top:58,fontSize:32,letterSpacing:3,fontWeight:500}}>BIO-SIGNATURE SCAN</div>
 <div style={{position:'absolute',top:111,left:48,right:48,height:1,background:'#508b8780'}}/>
 {[{name:'YAMETARO',img:'yametaro.png',value:5082,start:m.scannerTiming.yameStart,end:m.scannerTiming.yameEnd,color:'#ee7c6c',label:'ANOMALOUS'},{name:'FUKUGYUN',img:'fukuchan.png',value:213,start:m.scannerTiming.fukuStart,end:m.scannerTiming.fukuEnd,color:'#d9b77e',label:'ELEVATED'}].map((s,i)=>{const v=Math.round(ease(f,s.start,s.end,0,s.value));const done=f>=s.end;return <div key={s.name} style={{position:'absolute',left:48+i*604,top:134,width:580,height:420,background:'#07171bba',border:`1px solid ${done?s.color+'80':'#517e7e80'}`}}>
 <div style={{padding:'12px 20px',fontSize:18,letterSpacing:2,color:'#81aaa8',fontFamily:mono}}>SUBJECT 0{i+1}</div>
 <div style={{position:'relative',height:218,overflow:'hidden',margin:'0 16px'}}><Img src={staticFile(`aura/${s.img}`)} style={{width:'100%',height:'100%',objectFit:'contain',filter:'saturate(.3) contrast(1.15)'}}/>{!done&&<div style={{position:'absolute',top:(f*9)%216,left:0,right:0,height:2,background:'#c0ffef',boxShadow:'0 0 15px #90ffe9'}}/>}<div style={{position:'absolute',inset:0,background:'repeating-linear-gradient(transparent 0px, transparent 3px,#00222a22 4px)'}}/></div>
 <div style={{padding:'14px 20px 0',fontSize:28,letterSpacing:1.5}}>{s.name}</div><div style={{position:'absolute',right:20,top:268,fontSize:62,fontWeight:500,fontFamily:mono,letterSpacing:-4,color:s.color}}>{v.toLocaleString('en-US')}<span style={{fontSize:17,letterSpacing:0,marginLeft:7}}>MW</span></div>
 <div style={{margin:'14px 20px',fontFamily:mono,fontSize:18,letterSpacing:2,color:done?s.color:'#8aafad'}}>{done?s.label:f>=s.start?'ANALYZING':'PENDING'}</div>
 <div style={{position:'absolute',left:20,right:20,bottom:22,height:4,background:'#36575a'}}><div style={{height:'100%',width:`${Math.max(0,v/10247*100)}%`,background:s.color,boxShadow:`0 0 10px ${s.color}55`}}/></div>
 </div>})}
 <div style={{position:'absolute',top:572,left:48,right:48,display:'flex',justifyContent:'space-between',fontFamily:mono,fontSize:18,letterSpacing:.5}}><span style={{color:'#71918e'}}>BASELINE <b style={{color:'#c9d7cd'}}>10 MW</b></span><span style={{color:'#71918e'}}>ORIGIN <b style={{color:'#d3b17d'}}>10,247 MW</b></span></div>
 <div style={{position:'absolute',top:612,left:48,right:48,height:62,display:'flex',alignItems:'center',justifyContent:'center',background:danger?'#51221f70':'#15333380',borderTop:`1px solid ${danger?'#c87767':'#447a74'}`,borderBottom:'1px solid #526f6b40',color:danger?'#edb7a3':'#8db9b1',fontSize:26,letterSpacing:2.5,opacity:ease(f,12,24,0,1)}}>{f>=m.scannerTiming.retrievalFrame?'RETRIEVAL AUTHORIZED':'ANOMALY DETECTED'}</div>
 <div style={{position:'absolute',left:48,right:48,top:690,display:'flex',justifyContent:'space-between',fontFamily:mono,fontSize:14,letterSpacing:1.5,color:'#60837f'}}><span>REMOTE BIO-METRICS</span><span>{f>=m.scannerTiming.retrievalFrame?'CONTAINMENT / ACTIVE':'SIGNAL LOCK / CONFIRMED'}</span></div>
 </div></AbsoluteFill>};
const Scene=({s}:{s:Seg})=>{const f=useCurrentFrame();const g=s.fromFrame+f;const beat=m.music.beatFrames.find(b=>g>=b&&g<b+8);const hit=beat===undefined?0:Math.exp(-(g-beat)/2.2);const shake=g>=m.music.shatterFrame?hit:hit*.2;const sourceFrame=s.sourceStart+f*s.rate;
 // Only the very tight hologram face needs a wider lens. Every action shot fills 9:16.
 const close=(s.id==='hologram'&&sourceFrame>660)||(s.id==='windup'&&sourceFrame<754);
 const w=close?1180:1280*(s.file==='pov-full.mp4'?854/480:16/9);const h=w/(s.file==='pov-full.mp4'?854/480:16/9);const x=ease(f,0,s.duration-1,s.x0,s.x1);
 const mediaStyle:React.CSSProperties={position:'absolute',width:w,height:h,left:360-w*x,top:640-h/2,maxWidth:'none',filter:`contrast(${g>=m.music.shatterFrame?1.19:1.1}) saturate(.8) brightness(.98)`};
 const video=(ghost=false)=>s.id==='windup'&&f<6?<Img src={staticFile('aura/pre-impact.jpg')} style={mediaStyle}/>:<OffthreadVideo muted src={staticFile(`aura/${s.file}`)} startFrom={s.id==='windup'?748:s.sourceStart-(ghost?2:0)} playbackRate={s.id==='windup'?1:s.rate} style={mediaStyle}/>;
 return <AbsoluteFill style={{background:'#020b0d',overflow:'hidden'}}>
 {close&&<AbsoluteFill style={{transform:'scale(2.5)',filter:'blur(30px) brightness(.35)'}}>{video()}</AbsoluteFill>}
 <AbsoluteFill style={{transform:`translate(${Math.sin(g*2.7)*shake*14}px,${Math.cos(g*3.1)*shake*8}px) scale(${1+hit*.045+f/s.duration*.018})`}}>{video()}</AbsoluteFill>
 {g>=m.music.shatterFrame&&hit>.2&&<AbsoluteFill style={{opacity:hit*.17,mixBlendMode:'screen',filter:'hue-rotate(150deg)',transform:`translateX(${-hit*25}px) scale(1.025)`}}>{video(true)}</AbsoluteFill>}
 <AbsoluteFill style={{background:'linear-gradient(#00101920,transparent 30%,transparent 78%,#00101930)'}}/>
 </AbsoluteFill>};
const Film=()=>{const f=useCurrentFrame();const impact=f>=m.music.shatterFrame&&f<m.music.shatterFrame+6?1-(f-m.music.shatterFrame)/6:0;const sh=f-m.music.shatterFrame;
 return <AbsoluteFill style={{background:'#02090e',fontFamily:'Arial, sans-serif',overflow:'hidden'}}>
 {m.segments.map(s=><Sequence key={s.id} from={s.fromFrame} durationInFrames={s.duration}>{s.id==='scanner'?<Scanner/>:<Scene s={s}/>}</Sequence>)}
 {sh>=0&&sh<24&&<svg viewBox="0 0 720 1280" style={{position:'absolute',inset:0,opacity:(1-sh/24)*.7}}>{Array.from({length:14},(_,i)=>{const a=i*2.4;return <polygon key={i} points="-5,-24 10,4 -2,16" fill="#d5edf955" stroke="#e4f8ff77" strokeWidth=".6" transform={`translate(${360+Math.sin(a)*sh*(12+i%4)} ${640+Math.cos(a)*sh*(12+i%4)}) rotate(${i*30+sh*5})`}/>})}</svg>}
 {impact>0&&<AbsoluteFill style={{background:'#dcfff8',opacity:impact*.35,mixBlendMode:'screen'}}/>}
 <AbsoluteFill style={{boxShadow:'inset 0 0 105px #0005',pointerEvents:'none'}}/>
 <AbsoluteFill style={{background:'#000',opacity:f<5?ease(f,0,5,.25,0):ease(f,m.composition.durationInFrames-12,m.composition.durationInFrames-1,0,1)}}/>
 </AbsoluteFill>};
registerRoot(()=> <Composition id="SobayaHazardWideUI" component={Film} {...m.composition}/>);
