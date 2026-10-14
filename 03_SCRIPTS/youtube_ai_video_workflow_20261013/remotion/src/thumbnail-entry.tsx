import React from 'react';
import {AbsoluteFill,Composition,Img,registerRoot,staticFile} from 'remotion';
const GREEN='#07502f';
const Thumb=()=> <AbsoluteFill style={{background:'white',fontFamily:'"Hiragino Sans",sans-serif',color:'#002517'}}>
 <div style={{position:'absolute',top:0,left:0,right:0,height:54,textAlign:'center',fontSize:39,fontWeight:900,lineHeight:'54px'}}>Codex・Claude Code × Wan 3.0</div>
 <div style={{position:'absolute',left:0,right:0,top:54,height:496,display:'grid',gridTemplateColumns:'1fr 1fr',gridTemplateRows:'1fr 1fr',gap:3,background:'white'}}>{['arrest','anchor','home','office'].map(n=><div key={n} style={{overflow:'hidden',position:'relative'}}><Img src={staticFile(`thumbnail_${n}.png`)} style={{position:'absolute',width:'100%',height:'100%',objectFit:'cover',objectPosition:'center top'}}/></div>)}</div>
 <div style={{position:'absolute',left:0,top:54,background:GREEN,color:'white',fontWeight:900,fontSize:31,padding:'8px 20px'}}>AI動画の作り方</div>
 <div style={{position:'absolute',top:550,left:170,right:170,textAlign:'center'}}>
  <div style={{fontSize:43,fontWeight:900,lineHeight:1.45,whiteSpace:'nowrap'}}>いつものコーディングAIで、</div>
  <div style={{display:'inline-block',position:'relative',border:'5px solid #00A039',fontSize:67,fontWeight:900,lineHeight:1.15,padding:'0px 36px 4px'}}>動画まで。<div style={{position:'absolute',right:-10,bottom:-10,width:17,height:17,background:'#009838'}}/></div>
 </div>
 <Img src={staticFile('expressions/yametaro_happy_closed.png')} style={{position:'absolute',left:12,bottom:9,width:141,transform:'scaleX(-1)'}}/>
 <Img src={staticFile('expressions/takosan_happy_closed.png')} style={{position:'absolute',right:8,bottom:10,width:159}}/>
 </AbsoluteFill>;
registerRoot(()=> <Composition id="Thumbnail" component={Thumb} width={1280} height={720} fps={30} durationInFrames={1}/>);
