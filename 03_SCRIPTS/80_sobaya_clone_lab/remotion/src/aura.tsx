import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,Sequence,interpolate,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import m from './aura-manifest.json';
import {memberColor} from '../../../00_TEMPLATES/subtitles/member-colors';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const font='"Hiragino Sans", "Noto Sans JP", sans-serif';
const src=staticFile('aura/source.mp4');
const Scan=()=>{const f=useCurrentFrame();const n=Math.round(interpolate(f,[0,27],[0,5082],clamp));return <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 30%,#154640,#030c10 80%)',padding:'124px 52px',color:'#edfff8'}}>
 <div style={{fontSize:22,letterSpacing:9,color:'#7decd9'}}>窓際力研究所</div><div style={{fontSize:46,fontWeight:900,marginTop:18}}>その窓際力、規格外。</div>
 <Img src={staticFile('aura/yametaro.png')} style={{width:616,height:304,objectFit:'cover',marginTop:36,border:'1px solid #72ffe280'}}/>
 <div style={{display:'flex',justifyContent:'space-between',marginTop:18,fontSize:26}}><span>やめ太郎</span><span style={{color:'#ff6660'}}>{f>=27?'規格外':'測定中'}</span></div>
 <div style={{fontSize:130,lineHeight:1.15,fontWeight:900,letterSpacing:-5,color:f>=27?'#ff635c':'#b9ffe6',fontVariantNumeric:'tabular-nums'}}>{n.toLocaleString('en-US')}<span style={{fontSize:27,letterSpacing:0,marginLeft:18}}>MW</span></div>
 <div style={{display:'flex',alignItems:'center',gap:25,marginTop:32,borderTop:'1px solid #7decd940',paddingTop:24}}><Img src={staticFile('aura/fukuchan.png')} style={{width:190,height:100,objectFit:'cover'}}/><div><div style={{fontSize:23}}>福ギュン</div><div style={{fontSize:44,fontWeight:800,color:'#ffca78'}}>{Math.round(interpolate(f,[35,62],[0,213],clamp))} <span style={{fontSize:20}}>MW</span></div></div></div>
 <div style={{fontSize:21,marginTop:22,color:'#85a9a0'}}>標準窓際社員 10 MW ／ そば屋 10,247 MW</div></AbsoluteFill>};
const Shot=({start,rate=1,kind}:{start:number;rate?:number;kind:string})=>{const f=useCurrentFrame();const wide=kind==='escape'||(kind==='hologram'&&f>=110);const pos=kind==='break'?interpolate(f,[25,65],[50,18],clamp):50;const s=kind==='hologram'?1+Math.min(f,120)*.00055:1;
return <AbsoluteFill style={{transform:`scale(${s})`}}><OffthreadVideo muted src={src} startFrom={start} playbackRate={rate} style={{width:'100%',height:'100%',objectFit:'cover',objectPosition:`${pos}% 50%`,filter:wide?'blur(24px) brightness(.35)':'contrast(1.12) saturate(.85) brightness(.86)'}}/>{wide&&<><AbsoluteFill style={{background:'#02060ab0'}}/><OffthreadVideo muted src={src} startFrom={start} playbackRate={rate} style={{position:'absolute',width:1000,height:563,left:-140,top:270,objectFit:'cover',filter:'contrast(1.12) saturate(.85)'}}/></>}</AbsoluteFill>};
const Film=()=>{const f=useCurrentFrame();const beat=m.music.beatFrames.find(b=>f>=b&&f<b+8);const hit=beat===undefined?0:Math.exp(-(f-beat)/2.4);const main=f>=457&&f<463?1-(f-457)/6:0;const cap=m.captions.find(c=>f>=c.startFrame&&f<c.endFrame);
return <AbsoluteFill style={{background:'#020609',fontFamily:font,color:'white',overflow:'hidden'}}>
 <AbsoluteFill style={{transform:`translate(${Math.sin(f*2.7)*hit*9}px,${Math.cos(f*3.3)*hit*5}px) scale(${1+hit*.045})`}}>
 <Sequence durationInFrames={192}><Scan/></Sequence><Sequence from={192} durationInFrames={214}><Shot start={540} kind="hologram"/></Sequence>
 <Sequence from={406} durationInFrames={15}><Img src={staticFile('aura/hold.jpg')} style={{width:'100%',height:'100%',objectFit:'cover',filter:'contrast(1.3) saturate(.4)',transform:'scale(1.06)'}}/></Sequence>
 <Sequence from={421} durationInFrames={105}><Shot start={754} rate={5/7} kind="break"/></Sequence><Sequence from={526} durationInFrames={125}><Shot start={829} kind="escape"/></Sequence>
 <Sequence from={651} durationInFrames={30}><Img src={staticFile('aura/ending.jpg')} style={{width:'100%',height:'100%',objectFit:'cover',objectPosition:'25% center',filter:'contrast(1.3) saturate(.3)',transform:`scale(${1+(f-651)*.002})`}}/></Sequence></AbsoluteFill>
 {f>=192&&<AbsoluteFill style={{background:'linear-gradient(#00101860,transparent 28%,transparent 63%,#01050be8 92%)'}}/>}
 {f>=192&&<div style={{position:'absolute',left:42,top:106,fontSize:20,letterSpacing:6,color:'#d3f1edaa'}}>窓際力研究所</div>}
 {f>=421&&f<526&&<div style={{position:'absolute',top:175,left:42,right:42,fontSize:58,fontWeight:900,letterSpacing:7,textShadow:'0 3px 20px #000'}}>回収、開始。</div>}
 {cap&&<div style={{position:'absolute',left:42,right:72,top:1010,textAlign:'center',textShadow:'0 2px 10px #000'}}><div style={{fontSize:26,marginBottom:12}}>{cap.speaker}</div><div style={{fontSize:38,fontWeight:800,lineHeight:1.45,whiteSpace:'pre-line',WebkitTextStroke:`3px ${memberColor(cap.speaker)}`,paintOrder:'stroke fill'}}>{cap.text}</div></div>}
 {f>=651&&<div style={{position:'absolute',left:42,right:42,top:940,textAlign:'center',fontSize:76,fontWeight:900,letterSpacing:10,textShadow:'0 5px 30px #000'}}>規格外。</div>}
 <AbsoluteFill style={{pointerEvents:'none',boxShadow:'inset 0 0 150px #0008'}}/>{main>0&&<AbsoluteFill style={{background:'#d9fff3',opacity:main*.55,mixBlendMode:'screen'}}/>}
 <AbsoluteFill style={{background:'#010308',opacity:interpolate(f,[673,680],[0,1],clamp)}}/></AbsoluteFill>};
registerRoot(()=> <Composition id="CloneLabAuraShort" component={Film} {...m.composition}/>);
