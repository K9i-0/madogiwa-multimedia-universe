import React from 'react';
import {AbsoluteFill,Composition,Img,registerRoot,staticFile} from 'remotion';
const bold:React.CSSProperties={fontWeight:900,WebkitTextStroke:'14px #111',paintOrder:'stroke fill',textShadow:'0 9px 0 #111, 0 14px 22px #0009',letterSpacing:-5,whiteSpace:'nowrap'};
const Thumb=()=> <AbsoluteFill style={{background:'#101519',fontFamily:'"Hiragino Sans",sans-serif',color:'white'}}>
 <AbsoluteFill style={{display:'grid',gridTemplateColumns:'1fr 1fr',gridTemplateRows:'1fr 1fr',gap:4}}>{['arrest','anchor','home','office'].map(n=><div key={n} style={{overflow:'hidden',position:'relative'}}><Img src={staticFile(`thumbnail_${n}.png`)} style={{width:'100%',height:'100%',objectFit:'cover',objectPosition:'center top'}}/></div>)}</AbsoluteFill>
 <AbsoluteFill style={{background:'linear-gradient(180deg,#0007,#0008 60%,#0006)'}}/>
 <div style={{position:'absolute',top:25,left:35,right:35,textAlign:'center',fontSize:43,fontWeight:900,background:'#111e',padding:'10px 0',borderBottom:'6px solid #ffdc00'}}>Codex・Claude Code × Wan 3.0</div>
 <div style={{position:'absolute',top:160,left:0,right:0,textAlign:'center'}}>
  <div style={{...bold,fontSize:137,lineHeight:1.35}}>いつものAIで</div>
  <div style={{...bold,fontSize:190,lineHeight:1.3,color:'#ffe500'}}>動画まで。</div>
 </div>
 <Img src={staticFile('expressions/yametaro_happy_closed.png')} style={{position:'absolute',left:8,bottom:0,width:151,transform:'scaleX(-1)'}}/>
 <Img src={staticFile('expressions/takosan_happy_closed.png')} style={{position:'absolute',right:8,bottom:0,width:172}}/>
 <div style={{position:'absolute',bottom:25,left:290,right:290,textAlign:'center',fontSize:36,fontWeight:900,color:'#fff',background:'#d82722',padding:'9px 0',border:'3px solid #fff',boxShadow:'0 4px 0 #111'}}>チャットで始める動画制作</div>
 </AbsoluteFill>;
registerRoot(()=> <Composition id="Thumbnail" component={Thumb} width={1280} height={720} fps={30} durationInFrames={1}/>);
