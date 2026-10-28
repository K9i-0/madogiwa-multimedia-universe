import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import manifest from './edit-manifest.json';

const m=manifest;
const gothic='"Hiragino Kaku Gothic ProN", "Hiragino Sans", sans-serif';
const mincho='"Hiragino Mincho ProN", "YuMincho", serif';
const bevel='4px 4px 0 #638391, -3px -3px 0 #fff';
const stroke:React.CSSProperties={WebkitTextStroke:'3px #1c2130',paintOrder:'stroke fill',textShadow:'2px 2px 1px #222'};
const FitText=({children,style={}}:{children:React.ReactNode;style?:React.CSSProperties})=><div style={{fontFamily:gothic,whiteSpace:'pre-line',...style}}>{children}</div>;

const Mug=({mega=false,empty=false,width=210}:{mega?:boolean;empty?:boolean;width?:number})=><svg width={width} height={width*1.17} viewBox="0 0 240 280">
  <defs><linearGradient id={mega?'beerMega':'beerSmall'} x1="0" x2="1"><stop stopColor="#ba6d00"/><stop offset=".3" stopColor="#ffd760"/><stop offset="1" stopColor="#d69612"/></linearGradient></defs>
  <path d="M177 65h25q23 0 23 28v77q0 29-24 29h-24" fill="none" stroke="#869aa0" strokeWidth="17"/>
  <path d="M177 65h25q23 0 23 28v77q0 29-24 29h-24" fill="none" stroke="#eaf0ef" strokeWidth="8"/>
  <path d="M28 28h150v213q0 15-16 15H43q-15 0-15-15Z" fill="#e6eff0" fillOpacity=".6" stroke="#81959b" strokeWidth="5"/>
  {!empty&&<><path d="M35 74h136v165q0 9-10 9H45q-10 0-10-9Z" fill={`url(#${mega?'beerMega':'beerSmall'})`}/><path d="M35 36q15-14 29 0q12-11 25 0q17-15 32 0q12-10 24 0q12-9 26 0v44q-19-8-32 0q-20-7-36 0q-17-7-34 0q-18-7-34 0Z" fill="#fff8db"/><g fill="#fff3b3" opacity=".65"><circle cx="60" cy="125" r="4"/><circle cx="120" cy="160" r="3"/><circle cx="85" cy="210" r="4"/><circle cx="146" cy="109" r="3"/></g></>}
  <path d="M47 48v180M67 94v135M155 88v141" stroke="#fff" strokeWidth="6" opacity=".36"/>
  <ellipse cx="103" cy="258" rx="91" ry="8" fill="#1b343e" opacity=".15"/>
</svg>;

const AbstractBackground=()=>{
 const f=useCurrentFrame();return <AbsoluteFill style={{background:'linear-gradient(135deg,#0b2898 0%,#6967d0 47%,#154b98 100%)',overflow:'hidden'}}>
   {[0,1,2,3,4].map((n)=><div key={n} style={{position:'absolute',left:-220+n*240+Math.sin(f/95+n)*80,top:-150+(n%3)*230+Math.cos(f/75+n)*65,width:450,height:580,borderRadius:'50%',transform:`rotate(${n*37+f*.07}deg)`,background:`radial-gradient(ellipse at 30% 25%,rgba(218,204,255,.77),rgba(124,72,225,.44) 48%,rgba(0,35,131,.18) 70%)`,filter:'blur(4px)',opacity:.75}}/>)}
 </AbsoluteFill>;
};

const Opening=()=>{
 const f=useCurrentFrame();const opacity=interpolate(f,[5,22,117,139],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill><AbstractBackground/><AbsoluteFill style={{alignItems:'center',justifyContent:'center',opacity}}>
   <div style={{fontFamily:mincho,fontWeight:700,fontSize:64,color:'#ffffed',letterSpacing:5,...stroke}}>窓際マナー研修</div>
   <div style={{fontFamily:mincho,fontWeight:600,fontSize:37,color:'#fff',marginTop:36,...stroke}}>飲み会での気配り</div>
 </AbsoluteFill></AbsoluteFill>;
};

const Header=()=> <div style={{position:'absolute',left:32,top:26,right:32,height:65,background:'linear-gradient(#406eae,#183f83)',border:'2px solid #dce9f5',boxShadow:'3px 3px 0 #6b8096',display:'flex',alignItems:'center',padding:'0 24px',color:'#fff'}}>
 <FitText style={{fontSize:30,fontWeight:600}}>窓際マナー研修</FitText><FitText style={{marginLeft:'auto',fontSize:23}}>飲み会での気配り</FitText>
</div>;

const Explanation=({kind,local}:{kind:string;local:number})=>{
 const segmentStart=m.segments.find(s=>s.id===kind)!.start;
 const currentFrame=segmentStart+local;
 const consequence=m.captions.find(c=>c.text.replace(/\n/g,'').startsWith('職場に続いて酒席でも干す'));
 const consideration=m.captions.find(c=>c.text.replace(/\n/g,'').startsWith('相手のお立場に配慮'));
 const showConsequence=!!consequence&&currentFrame>=consequence.start;
 const showConsideration=!!consideration&&currentFrame>=consideration.start;
 let panel:React.ReactNode;
 if(kind==='explain01')panel=<>
   <div style={{position:'absolute',left:40,top:139,width:552,height:414,border:'3px solid #fff',boxShadow:bevel,overflow:'hidden'}}><Img src={staticFile('still.png')} style={{width:'100%',height:'100%',objectFit:'cover'}}/></div>
   <div style={{position:'absolute',left:626,top:144,width:290,textAlign:'center'}}>
    <FitText style={{fontSize:25,color:'#163861',borderBottom:'2px solid #78909a',paddingBottom:12}}>ここがポイント</FitText>
    <Mug mega width={215}/><FitText style={{fontSize:34,fontWeight:700,color:'#ac1719',marginTop:-8}}>メガジョッキ</FitText>
    <FitText style={{fontSize:25,lineHeight:1.5,marginTop:14}}>窓際社員には<br/>大きなジョッキを</FitText>
   </div>
 </>;
 else if(kind==='explain02')panel=<>
   <FitText style={{position:'absolute',top:124,left:60,fontSize:33,color:'#123e78'}}>通常のジョッキでは……</FitText>
   <div style={{position:'absolute',left:122,top:217}}><Mug width={220}/></div>
   <div style={{position:'absolute',left:424,top:310,fontSize:74,color:'#a34c2e'}}>→</div>
   <div style={{position:'absolute',left:605,top:217}}><Mug empty width={220}/></div>
   <FitText style={{position:'absolute',left:0,right:0,top:518,textAlign:'center',fontSize:35,color:'#ad161b',fontWeight:700}}>すぐに「飲み干される」</FitText>
 </>;
 else if(kind==='explain03')panel=<>
   <div style={{position:'absolute',top:145,left:65,width:350,height:237,background:'#f1f3ef',boxShadow:bevel,textAlign:'center',paddingTop:28}}>
    <FitText style={{fontSize:27,color:'#3b4d5b'}}>{showConsequence?'職場':'酒席'}</FitText><FitText style={{fontSize:44,marginTop:44,color:'#393939'}}>{showConsequence?'干す':'飲み干す'}</FitText>
   </div>
   <div style={{position:'absolute',top:247,left:452,fontSize:49,color:'#1d3c5c'}}>{showConsequence?'＋':'→'}</div>
   <div style={{position:'absolute',top:145,left:546,width:350,height:237,background:'#f1f3ef',boxShadow:bevel,textAlign:'center',paddingTop:28}}>
    <FitText style={{fontSize:27,color:'#3b4d5b'}}>{showConsequence?'酒席':'職場'}</FitText><FitText style={{fontSize:44,marginTop:44,color:'#393939'}}>{showConsequence?'飲み干す':'干す'}</FitText>
   </div>
   <FitText style={{position:'absolute',top:445,left:60,right:60,textAlign:'center',fontSize:43,fontWeight:700,color:'#ae161c',textShadow:'2px 2px #fff'}}>{showConsideration?'相手のお立場に配慮しましょう':showConsequence?'重ねて失礼に当たります':'「干す」を連想させてしまいます'}</FitText>
 </>;
 else panel=<>
   <div style={{position:'absolute',left:48,top:128,width:414,height:430,background:'#eff0e6',boxShadow:bevel,textAlign:'center'}}>
    <FitText style={{fontSize:30,background:'#a3b8c8',padding:13,color:'#203145'}}>一般社員</FitText><div style={{height:292,display:'flex',alignItems:'flex-end',justifyContent:'center'}}><Mug width={160}/></div><FitText style={{fontSize:29,marginTop:11}}>通常のジョッキ</FitText>
   </div>
   <div style={{position:'absolute',left:498,top:128,width:414,height:430,background:'#f5f0d5',boxShadow:bevel,textAlign:'center'}}>
    <FitText style={{fontSize:30,background:'#e4c65b',padding:13,color:'#4c3810'}}>窓際社員</FitText><div style={{height:292,display:'flex',alignItems:'flex-end',justifyContent:'center'}}><Mug mega width={246}/></div><FitText style={{fontSize:29,marginTop:11,color:'#a61818',fontWeight:700}}>メガジョッキ</FitText>
   </div>
 </>;
 return <AbsoluteFill style={{background:'linear-gradient(135deg,#dbe5e9,#b8ced4)',color:'#222'}}><Header/>{panel}</AbsoluteFill>;
};

const Film=()=>{
 const frame=useCurrentFrame();
 const segment=m.segments.find(s=>frame>=s.start&&frame<s.start+s.duration)!;
 const local=frame-segment.start;
 const caption=m.captions.find(c=>frame>=c.start&&frame<c.end);
 let body:React.ReactNode;
 if(segment.type==='opening')body=<Opening/>;
 else if(segment.type==='scene')body=<><Sequence from={segment.start}><OffthreadVideo src={staticFile('scene.mp4')} muted style={{width:'100%',height:'100%',objectFit:'contain'}}/></Sequence><div style={{position:'absolute',right:40,bottom:43,textAlign:'right',color:'#fff',...stroke}}><FitText style={{fontSize:20,color:'#b2d4ef'}}>窓際マナー研修</FitText><FitText style={{fontSize:26}}>「飲み会での気配り」</FitText></div></>;
 else if(segment.type==='chapter')body=<AbsoluteFill style={{background:'#2464ac',justifyContent:'center',alignItems:'center',color:'#e8f1ff',fontSize:41,fontFamily:gothic}}>「メガジョッキ」</AbsoluteFill>;
 else if(segment.type==='ending')body=<AbsoluteFill><AbstractBackground/><AbsoluteFill style={{justifyContent:'center',alignItems:'center',color:'#ffffed',fontFamily:mincho,fontSize:45,fontWeight:600,lineHeight:1.8,textAlign:'center',...stroke}}>職場に続いて、<br/>酒席でも干さない。</AbsoluteFill></AbsoluteFill>;
 else body=<Explanation kind={segment.id} local={local}/>;
 const fade=interpolate(frame,[m.composition.durationInFrames-24,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{background:'#05070a',fontFamily:gothic,fontSynthesis:'none',overflow:'hidden'}}>
   <AbsoluteFill style={{filter:'contrast(.94) saturate(.80) blur(.45px)'}}>{body}
    {caption&&<div style={{position:'absolute',left:33,right:33,bottom:28,minHeight:89,padding:'10px 18px',boxSizing:'border-box',display:'flex',alignItems:'center',justifyContent:'center',background:'#173861',border:'2px solid #bccedf',boxShadow:'3px 3px 0 #6b7c89',color:'#fff',textAlign:'center',fontSize:28,lineHeight:1.46,whiteSpace:'pre-line'}}>{caption.text}</div>}
   </AbsoluteFill>
   <AbsoluteFill style={{pointerEvents:'none',opacity:.025,background:'repeating-linear-gradient(0deg,transparent,transparent 2px,#10214d 3px,transparent 4px)'}}/>
   <AbsoluteFill style={{background:'#000',opacity:fade}}/>
 </AbsoluteFill>;
};

export const Root=()=> <Composition id="MegaMugDVD" component={Film} width={m.composition.width} height={m.composition.height} fps={m.composition.fps} durationInFrames={m.composition.durationInFrames}/>;
