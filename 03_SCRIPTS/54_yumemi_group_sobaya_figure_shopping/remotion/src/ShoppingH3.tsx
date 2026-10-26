import React from 'react';
import {AbsoluteFill,Audio,OffthreadVideo,Sequence,interpolate,staticFile,useCurrentFrame} from 'remotion';
import {memberColors} from '../../../00_TEMPLATES/subtitles/member-colors';
import m from './edit-manifest-h3.json';
const wine='#7b1735', gold='#e1b85e', ink='#302027';
const ease=(f:number,a:number,b:number)=>interpolate(f,[a,a+5,b-5,b],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
const Panel:React.FC<{children:React.ReactNode;style?:React.CSSProperties}>=({children,style})=><div style={{background:'rgba(255,252,244,.96)',borderLeft:`5px solid ${gold}`,padding:'13px 20px',boxShadow:'0 4px 18px #0003',color:ink,...style}}>{children}</div>;
export function ShoppingH3(){
 const f=useCurrentFrame(),c=m.cues;
 const caption=m.captions.find(x=>f>=x.startFrame&&f<x.endFrame);
 const active=(r:{startFrame:number;endFrame:number})=>f>=r.startFrame&&f<r.endFrame;
 const color=caption?.speaker==='そば屋'?memberColors.sobaya:memberColors.fukuchan;
 return <AbsoluteFill style={{backgroundColor:'#000',fontFamily:'Hiragino Sans, sans-serif',fontSynthesis:'none'}}>
  <Sequence from={0} durationInFrames={360}><OffthreadVideo src={staticFile('h3/ch01_768p.mp4')} muted style={{width:'100%',height:'100%'}}/></Sequence>
  <Sequence from={360} durationInFrames={360}><OffthreadVideo src={staticFile('h3/ch02_768p.mp4')} muted style={{width:'100%',height:'100%'}}/></Sequence>
  <Audio src={staticFile(m.replacementAudio)}/>
  <div style={{position:'absolute',left:44,top:30,display:'flex',alignItems:'center',gap:10,padding:'8px 17px 8px 10px',borderRadius:6,background:'rgba(255,252,244,.95)',boxShadow:'0 3px 12px #0002',color:wine}}>
   <span style={{background:wine,color:'#fff',borderRadius:'50%',width:30,height:30,textAlign:'center',fontSize:21,lineHeight:'30px'}}>ゆ</span><span style={{fontSize:25,fontWeight:600}}>ゆめみグループ</span>
  </div>
  <div style={{position:'absolute',right:44,top:32,color:'#fff',background:wine,borderBottom:`3px solid ${gold}`,padding:'8px 17px',fontSize:23,fontWeight:600}}>本日限り</div>
  {active(c.intro)&&<Panel style={{position:'absolute',left:48,bottom:88,opacity:ease(f,c.intro.startFrame,c.intro.endFrame)}}>
   <div style={{fontSize:20,color:wine,marginBottom:5}}>本日の特別商品</div><div style={{fontSize:36,fontWeight:600}}>等身大そば屋フィギュア</div>
  </Panel>}
  {active(c.features)&&<Panel style={{position:'absolute',left:48,bottom:132,opacity:ease(f,c.features.startFrame,c.features.endFrame)}}>
   <div style={{fontSize:27,fontWeight:600}}>職人完全監修 · 超高品質FRP</div><div style={{fontSize:20,marginTop:7}}>身長180cm ／ 重量100kg</div>
  </Panel>}
  {active(c.president)&&<Panel style={{position:'absolute',right:48,bottom:132,opacity:ease(f,c.president.startFrame,c.president.endFrame),fontSize:24}}>ゆめみグループ社長　<strong>とーくん</strong></Panel>}
  {active(c.priceReveal)&&<Panel style={{position:'absolute',left:44,top:108,width:390,opacity:ease(f,c.priceReveal.startFrame,c.priceReveal.endFrame)}}>
   <div style={{fontSize:21,color:'#6c6063'}}>通常価格 <span style={{textDecoration:'line-through'}}>1,238,000円</span></div>
   <div style={{display:'block',marginTop:6}}><span style={{display:'block',fontSize:19,color:wine,fontWeight:600,marginBottom:3}}>本日価格</span><span style={{fontSize:59,fontWeight:700,color:wine,letterSpacing:-2,whiteSpace:'nowrap'}}>198,000<span style={{fontSize:31,letterSpacing:0}}>円</span></span></div>
  </Panel>}
  {f>=c.priceReveal.endFrame&&f<c.comparison.startFrame&&<Panel style={{position:'absolute',right:44,top:88,padding:'8px 14px',fontSize:27,fontWeight:600,color:wine}}><span style={{fontSize:17,marginRight:8}}>本日価格</span>198,000円</Panel>}
  {active(c.comparison)&&<Panel style={{position:'absolute',left:48,bottom:133,padding:'9px 17px',fontSize:25,opacity:ease(f,c.comparison.startFrame,c.comparison.endFrame)}}>本人一致率 <strong style={{color:wine}}>99.9%</strong></Panel>}
  {active(c.disclaimer)&&<div style={{position:'absolute',left:48,bottom:42,fontSize:20,color:'#fff',textShadow:'0 2px 4px #000, 0 0 4px #000'}}>※品質の感じ方には個人差があります</div>}
  {caption&&<>
   <div style={{position:'absolute',left:0,right:0,bottom:0,height:115,background:'linear-gradient(transparent,rgba(0,0,0,.65))'}}/>
   <div style={{position:'absolute',left:50,right:50,bottom:38,textAlign:'center',fontSize:caption.speaker==='そば屋'?43:35,fontWeight:600,lineHeight:1.3,color:'#fffdf7',WebkitTextStroke:`4px ${color}`,paintOrder:'stroke fill',filter:'drop-shadow(0 2px 2px #000)',whiteSpace:'nowrap'}}>{caption.text}</div>
  </>}
  {active(c.final)&&<Panel style={{position:'absolute',left:48,right:48,bottom:42,display:'flex',justifyContent:'space-between',alignItems:'center',opacity:ease(f,c.final.startFrame,c.final.endFrame)}}><span style={{fontSize:26}}>等身大そば屋フィギュア　<strong style={{color:wine}}>198,000円</strong></span><strong style={{fontSize:38,color:wine}}>残り2体！</strong></Panel>}
 </AbsoluteFill>;
}
