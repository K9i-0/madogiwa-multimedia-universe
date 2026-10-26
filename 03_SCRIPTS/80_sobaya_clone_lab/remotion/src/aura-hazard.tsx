import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,Sequence,interpolate,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import m from './aura-hazard.json';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const ease=(f:number,a:number,b:number,x:number,y:number)=>interpolate(f,[a,b],[x,y],clamp);
const mono='"SFMono-Regular", Menlo, monospace';
type Seg=typeof m.segments[number];
const Scanner=()=>{const f=useCurrentFrame();const danger=f>=24;return <AbsoluteFill style={{background:'radial-gradient(ellipse at 40% 35%,#133132,#020a0e 80%)',padding:36,color:'#c6e0df'}}>
 <svg viewBox="0 0 720 1280" style={{position:'absolute',inset:0,opacity:.16}}>{Array.from({length:19},(_,i)=><path key={i} d={`M 0 ${i*70} H 720 M ${i*70} 0 V 1280`} stroke="#407d7a" strokeWidth=".5"/>)}</svg>
 <div style={{position:'absolute',left:38,right:38,top:160,display:'flex',justifyContent:'space-between',fontFamily:mono,fontSize:15,letterSpacing:2,color:'#679f9c'}}><span>TAKO LAB / 07</span><span style={{color:'#9ff2db'}}>● LIVE</span></div>
 <div style={{position:'absolute',left:38,top:203,fontSize:27,letterSpacing:3,fontWeight:500}}>BIO-SIGNATURE SCAN</div>
 <div style={{position:'absolute',top:258,left:38,right:38,height:1,background:'#508b8780'}}/>
 {[{name:'YAMETARO',img:'yametaro.png',value:5082,start:0,end:24,color:'#ee7c6c',label:'ANOMALOUS'},{name:'FUKUGYUN',img:'fukuchan.png',value:213,start:35,end:66,color:'#d9b77e',label:'ELEVATED'}].map((s,i)=>{const v=Math.round(ease(f,s.start,s.end,0,s.value));const done=f>=s.end;return <div key={s.name} style={{position:'absolute',left:38+i*330,top:304,width:314,height:501,background:'#07171bba',border:`1px solid ${done?s.color+'80':'#517e7e80'}`}}>
 <div style={{padding:'18px 15px',fontSize:17,letterSpacing:2,color:'#81aaa8',fontFamily:mono}}>SUBJECT 0{i+1}</div>
 <div style={{position:'relative',height:170,overflow:'hidden',margin:'0 8px'}}><Img src={staticFile(`aura/${s.img}`)} style={{width:'100%',height:'100%',objectFit:'cover',filter:'saturate(.3) contrast(1.15)'}}/>{!done&&<div style={{position:'absolute',top:(f*7)%168,left:0,right:0,height:2,background:'#c0ffef',boxShadow:'0 0 15px #90ffe9'}}/>}<div style={{position:'absolute',inset:0,background:'repeating-linear-gradient(transparent 0px, transparent 3px,#00222a22 4px)'}}/></div>
 <div style={{padding:'22px 15px 0',fontSize:22,letterSpacing:1.5}}>{s.name}</div><div style={{padding:'10px 15px',fontSize:70,fontWeight:500,fontFamily:mono,letterSpacing:-4,color:s.color}}>{v.toLocaleString('en-US')}<span style={{fontSize:17,letterSpacing:0,marginLeft:7}}>MW</span></div>
 <div style={{margin:'5px 15px',fontFamily:mono,fontSize:13,letterSpacing:2,color:done?s.color:'#8aafad'}}>{done?s.label:f>=s.start?'ANALYZING':'PENDING'}</div>
 <div style={{position:'absolute',left:15,right:15,bottom:22,height:4,background:'#36575a'}}><div style={{height:'100%',width:`${Math.max(0,v/10247*100)}%`,background:s.color,boxShadow:`0 0 10px ${s.color}55`}}/></div>
 </div>})}
 <div style={{position:'absolute',top:851,left:38,right:38,display:'flex',justifyContent:'space-between',fontFamily:mono,fontSize:15,letterSpacing:.5}}><span style={{color:'#71918e'}}>BASELINE <b style={{color:'#c9d7cd'}}>10 MW</b></span><span style={{color:'#71918e'}}>ORIGIN <b style={{color:'#d3b17d'}}>10,247 MW</b></span></div>
 <div style={{position:'absolute',top:912,left:38,right:38,height:98,display:'flex',alignItems:'center',justifyContent:'center',background:danger?'#51221f70':'#15333380',borderTop:`1px solid ${danger?'#c87767':'#447a74'}`,borderBottom:'1px solid #526f6b40',color:danger?'#edb7a3':'#8db9b1',fontSize:23,letterSpacing:2.5,opacity:ease(f,12,24,0,1)}}>{f>=110?'RETRIEVAL AUTHORIZED':'ANOMALY DETECTED'}</div>
 <div style={{position:'absolute',left:38,right:38,top:1050,display:'flex',justifyContent:'space-between',fontFamily:mono,fontSize:12,letterSpacing:1.5,color:'#60837f'}}><span>REMOTE BIO-METRICS</span><span>{f>=110?'CONTAINMENT / ACTIVE':'SIGNAL LOCK / CONFIRMED'}</span></div>
 </AbsoluteFill>};
const Scene=({s}:{s:Seg})=>{const f=useCurrentFrame();const g=s.fromFrame+f;const beat=m.music.beatFrames.find(b=>g>=b&&g<b+8);const hit=beat===undefined?0:Math.exp(-(g-beat)/2.2);const shake=g>=720?hit:hit*.2;const sourceFrame=s.sourceStart+f*s.rate;
 // Only the very tight hologram face needs a wider lens. Every action shot fills 9:16.
 const close=(s.id==='hologram'&&sourceFrame>660)||(s.id==='windup'&&sourceFrame<754);
 const w=close?1180:1280*(s.file==='pov-full.mp4'?854/480:16/9);const h=w/(s.file==='pov-full.mp4'?854/480:16/9);const x=ease(f,0,s.duration-1,s.x0,s.x1);
 const mediaStyle:React.CSSProperties={position:'absolute',width:w,height:h,left:360-w*x,top:640-h/2,maxWidth:'none',filter:`contrast(${g>=720?1.19:1.1}) saturate(.8) brightness(.98)`};
 const video=(ghost=false)=><OffthreadVideo muted src={staticFile(`aura/${s.file}`)} startFrom={s.sourceStart-(ghost?2:0)} playbackRate={s.rate} style={mediaStyle}/>;
 return <AbsoluteFill style={{background:'#020b0d',overflow:'hidden'}}>
 {close&&<AbsoluteFill style={{transform:'scale(2.5)',filter:'blur(30px) brightness(.35)'}}>{video()}</AbsoluteFill>}
 <AbsoluteFill style={{transform:`translate(${Math.sin(g*2.7)*shake*14}px,${Math.cos(g*3.1)*shake*8}px) scale(${1+hit*.045+f/s.duration*.018})`}}>{video()}</AbsoluteFill>
 {g>=720&&hit>.2&&<AbsoluteFill style={{opacity:hit*.17,mixBlendMode:'screen',filter:'hue-rotate(150deg)',transform:`translateX(${-hit*25}px) scale(1.025)`}}>{video(true)}</AbsoluteFill>}
 <AbsoluteFill style={{background:'linear-gradient(#00101920,transparent 30%,transparent 78%,#00101930)'}}/>
 </AbsoluteFill>};
const Title=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 55%,#173238,#02070a 70%)',justifyContent:'center',alignItems:'center'}}>
 <svg viewBox="0 0 720 1280" style={{position:'absolute',inset:0,opacity:.3}}>{Array.from({length:22},(_,i)=><path key={i} d={`M ${360+Math.sin(i*2.4)*150} ${640+Math.cos(i*2.4)*150} l ${Math.sin(i*2.4)*800} ${Math.cos(i*2.4)*800}`} stroke="#7cb6c0" strokeWidth=".6" transform={`rotate(${f*.05} 360 640)`}/>)}</svg>
 <div style={{textAlign:'center',transform:`perspective(900px) rotateX(${ease(f,0,13,35,0)}deg) scale(${ease(f,0,17,1.45,1)})`,filter:`blur(${ease(f,0,8,12,0)}px)`,opacity:ease(f,0,7,0,1),textShadow:'0 0 45px #5ac1cc44'}}><div style={{fontFamily:'Impact, Arial Narrow, sans-serif',fontSize:91,letterSpacing:8,color:'#dae7e7'}}>SOBAYA</div><div style={{fontFamily:'Impact, Arial Narrow, sans-serif',fontSize:117,letterSpacing:7,lineHeight:1.04,color:'#e8c8a3'}}>HAZARD</div><div style={{margin:'28px auto',height:2,width:230,background:'linear-gradient(90deg,transparent,#d1a575,transparent)',transform:`scaleX(${ease(f,0,20,0,1)})`}}/></div>
 </AbsoluteFill>};
const Film=()=>{const f=useCurrentFrame();const impact=f>=720&&f<726?1-(f-720)/6:0;const sh=f-720;
 return <AbsoluteFill style={{background:'#02090e',fontFamily:'Arial, sans-serif',overflow:'hidden'}}>
 {m.segments.map(s=><Sequence key={s.id} from={s.fromFrame} durationInFrames={s.duration}>{s.id==='scanner'?<Scanner/>:s.id==='title'?<Title/>:<Scene s={s}/>}</Sequence>)}
 {sh>=0&&sh<24&&<svg viewBox="0 0 720 1280" style={{position:'absolute',inset:0,opacity:(1-sh/24)*.7}}>{Array.from({length:14},(_,i)=>{const a=i*2.4;return <polygon key={i} points="-5,-24 10,4 -2,16" fill="#d5edf955" stroke="#e4f8ff77" strokeWidth=".6" transform={`translate(${360+Math.sin(a)*sh*(12+i%4)} ${640+Math.cos(a)*sh*(12+i%4)}) rotate(${i*30+sh*5})`}/>})}</svg>}
 {impact>0&&<AbsoluteFill style={{background:'#dcfff8',opacity:impact*.35,mixBlendMode:'screen'}}/>}
 <AbsoluteFill style={{boxShadow:'inset 0 0 105px #0005',pointerEvents:'none'}}/>
 <AbsoluteFill style={{background:'#000',opacity:f<5?ease(f,0,5,.25,0):ease(f,961,971,0,1)}}/>
 </AbsoluteFill>};
registerRoot(()=> <Composition id="SobayaHazardAura" component={Film} {...m.composition}/>);
