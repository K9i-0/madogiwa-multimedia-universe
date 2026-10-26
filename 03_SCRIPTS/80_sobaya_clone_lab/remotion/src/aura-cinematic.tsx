import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,Sequence,interpolate,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import m from './aura-cinematic.json';
const C={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const lerp=(f:number,a:number,b:number,x:number,y:number)=>interpolate(f,[a,b],[x,y],C);
const source=staticFile('aura/source.mp4');
type Segment=typeof m.segments[number];
const Scanner=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{background:'radial-gradient(ellipse,#12362f,#02090d 80%)'}}>
 <Img src={staticFile('aura/yametaro.png')} style={{position:'absolute',left:-120,top:290,width:960,height:473,filter:'saturate(.25) contrast(1.3)'}}/>
 <div style={{position:'absolute',left:65,right:65,top:280,height:490,border:'1px solid #a3f5d866',boxShadow:'0 0 50px #6affe012'}}/>
 <div style={{position:'absolute',left:65,right:65,top:300+((f*12)%450),height:2,background:'#c6ffed',boxShadow:'0 0 26px 5px #51ffd788'}}/>
 <div style={{position:'absolute',top:807,left:40,right:40,textAlign:'center',fontFamily:'Arial',fontWeight:700,fontSize:110,letterSpacing:6,color:'#f87169',textShadow:'0 0 34px #ef483566'}}>{Math.round(lerp(f,0,20,0,5082)).toLocaleString('en-US')}</div>
 {f>=16&&<div style={{position:'absolute',top:977,left:25,right:25,fontSize:26,letterSpacing:5,textAlign:'center',color:'#e5c0ab',opacity:lerp(f,16,23,0,1)}}>ANOMALY DETECTED</div>}
 </AbsoluteFill>};
const Scene=({s}:{s:Segment})=>{const f=useCurrentFrame();const global=s.from+f;const action=global>=485;const beat=m.music.beatFrames.find(b=>global>=b&&global<b+10);const hit=beat===undefined?0:Math.exp(-(global-beat)/2.5);const enter=s.from>=330?Math.exp(-f/3.5):0;const x=lerp(f,0,s.duration-1,s.x0,s.x1);const z=1+f/s.duration*.035+hit*.065+enter*.09;
 const imageStyle:React.CSSProperties={position:'absolute',width:s.width,height:s.width*9/16,maxWidth:'none',left:360-s.width*x,top:640-s.width*9/32,objectFit:'cover',filter:`contrast(${action?1.22:1.12}) saturate(${action?.8:.73}) brightness(.95)`};
 const pic=(ghost=false)=>s.rate===0?<Img src={staticFile(s.id==='title'?'aura/ending.jpg':'aura/command-hold.jpg')} style={imageStyle}/>:<OffthreadVideo muted src={source} startFrom={Math.max(0,s.sourceStart-(ghost?2:0))} playbackRate={s.rate} style={imageStyle}/>;
 if(s.id==='scan')return <Scanner/>;
 return <AbsoluteFill style={{overflow:'hidden',background:'#020709'}}>
 <AbsoluteFill style={{opacity:.4,transform:'scale(1.9)',filter:'blur(32px) brightness(.4)'}}>{pic()}</AbsoluteFill>
 <AbsoluteFill style={{transform:`translate(${(Math.sin(global*2.7)*hit*17)+(s.from>=755?enter*110:0)}px,${Math.cos(global*3.5)*hit*10}px) rotate(${hit*Math.sin(global)*.55}deg) scale(${z})`}}>{pic()}</AbsoluteFill>
 {action&&hit>.18&&<AbsoluteFill style={{opacity:hit*.24,mixBlendMode:'screen',transform:`translate(${-hit*40}px,${hit*8}px) scale(${z*1.02})`,filter:'hue-rotate(130deg) blur(1px)'}}>{pic(true)}</AbsoluteFill>}
 <AbsoluteFill style={{background:'linear-gradient(#01060c40,transparent 28%,transparent 72%,#01060c88)'}}/>
 </AbsoluteFill>};
const Title=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{justifyContent:'center',alignItems:'center',paddingBottom:40,background:`linear-gradient(transparent,#010509${Math.round(lerp(f,0,18,70,215)).toString(16)} 55%,#010509)`}}>
 <div style={{textAlign:'center',transform:`perspective(800px) rotateX(${lerp(f,0,16,55,0)}deg) scale(${lerp(f,0,18,1.65,1)})`,filter:`blur(${lerp(f,0,10,15,0)}px)`,opacity:lerp(f,0,8,0,1),textShadow:'0 0 40px #9deddd50'}}><div style={{fontFamily:'Impact, Arial Narrow, sans-serif',fontSize:126,lineHeight:.95,letterSpacing:lerp(f,0,25,28,8),color:'#e7f4ef'}}>CLONE<br/>LAB</div><div style={{height:2,width:220,margin:'36px auto 0',background:'linear-gradient(90deg,transparent,#e1a86a,transparent)',transform:`scaleX(${lerp(f,5,25,0,1)})`}}/></div>
 </AbsoluteFill>};
const Film=()=>{const f=useCurrentFrame();const impacts=[485,755,800,845,890,935,980];const impact=impacts.find(b=>f>=b&&f<b+7);const p=impact===undefined?0:1-(f-impact)/7;const sh=f-485;const bars=lerp(f,465,485,100,45);
 return <AbsoluteFill style={{background:'#010609',color:'#eaf5ef',fontFamily:'Arial, sans-serif',overflow:'hidden'}}>
 {m.segments.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.duration}><Scene s={s}/></Sequence>)}
 <AbsoluteFill style={{boxShadow:'inset 0 0 160px #0009',pointerEvents:'none'}}/>
 {sh>=0&&sh<33&&<svg viewBox="0 0 720 1280" style={{position:'absolute',width:720,height:1280,opacity:1-sh/33,pointerEvents:'none'}}>{Array.from({length:18},(_,i)=>{const a=i*2.4;const distance=sh*(9+i%5);const x=360+Math.sin(a)*distance,y=640+Math.cos(a)*distance;return <polygon key={i} points="-7,-32 11,4 -4,20" fill={i%2?'#91d8e76a':'#ffe0ab80'} stroke="#d7f3fc88" strokeWidth=".6" transform={`translate(${x} ${y}) rotate(${i*39+sh*6}) scale(${.5+i%4*.3})`}/>})}</svg>}
 {p>0&&<><AbsoluteFill style={{background:f===485?'#d9f7f2':'#82d3e6',opacity:p*(impact===485?.52:.18),mixBlendMode:'screen'}}/><div style={{position:'absolute',left:-100,right:-100,top:550,height:3,background:'#a6e7fa',boxShadow:'0 0 25px 12px #9bdafa80',opacity:p*.65,transform:`translateY(${(1-p)*160}px)`}}/></>}
 <div style={{position:'absolute',top:0,width:'100%',height:bars,background:'#010609'}}/><div style={{position:'absolute',bottom:0,width:'100%',height:bars,background:'#010609'}}/>
 <Sequence from={980} durationInFrames={70}><Title/></Sequence>
 <AbsoluteFill style={{background:'#000',opacity:f<8?lerp(f,0,8,.5,0):lerp(f,1036,1049,0,1)}}/>
 </AbsoluteFill>};
registerRoot(()=> <Composition id="CloneLabCinematic" component={Film} {...m.composition}/>);
