import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {ThumbnailModelV1} from './ThumbnailModelV1';

export const ThumbnailActualV1 = () => <AbsoluteFill style={{background:'#f3eee5',fontFamily:'"Hiragino Sans",sans-serif',color:'#103b2a'}}>
  <div style={{position:'absolute',left:640,top:115,width:640,height:605,background:'#263831'}}>
    <ThumbnailModelV1 kind="sobaya" mode="turn" t={2.8} freeze width={640} height={560} zoom={1.14}/>
  </div>
  <div style={{position:'absolute',left:110,top:139,width:430,height:440,overflow:'hidden'}}>
    <Img src={staticFile('sobaya_reference_v4.png')} style={{position:'absolute',width:1805.76,height:1016.28,maxWidth:'none',left:0,top:-119}}/>
  </div>
  <div style={{position:'absolute',left:0,top:0,width:1280,height:119,background:'#fff',display:'flex',alignItems:'center',justifyContent:'center',gap:26,borderBottom:'5px solid #176b47'}}>
    <Img src={staticFile('webrefs_v3/openai_icon.svg')} style={{width:73,height:73,colorScheme:'light'}}/>
    <span style={{fontSize:66,fontWeight:800,letterSpacing:-2}}>Codex</span>
    <span style={{fontSize:65,fontWeight:500,margin:'0 6px'}}>×</span>
    <Img src={staticFile('webrefs_v3/tripo_logo.svg')} style={{width:346,height:84,objectFit:'contain'}}/>
  </div>
  <div style={{position:'absolute',left:40,top:144,background:'#fff',padding:'10px 25px',fontSize:35,fontWeight:800,boxShadow:'0 3px 12px #0001'}}>元画像</div>
  <div style={{position:'absolute',left:665,top:144,background:'#f8db34',padding:'10px 22px',fontSize:31,fontWeight:800}}>3Dモデル</div>
  <svg width="1280" height="720" style={{position:'absolute',inset:0}}>
    <path d="M582 333 H638 V302 L697 362 L638 422 V391 H582 Z" fill="#ffdd22" stroke="#fff" strokeWidth="7" strokeLinejoin="round"/>
  </svg>
  <div style={{position:'absolute',left:0,right:0,bottom:0,height:157,background:'#103b2a',borderTop:'6px solid #f8db34'}}/>
  <div style={{position:'absolute',left:138,right:138,bottom:41,textAlign:'center',whiteSpace:'nowrap',lineHeight:1.2,fontSize:70,fontWeight:900,letterSpacing:-4,color:'#fff',textShadow:'0 3px 0 #0004'}}>自分のキャラを<span style={{color:'#ffdf28',fontSize:84}}>3D</span>に！</div>
  <Img src={staticFile('expressions/yametaro_happy_closed.png')} style={{position:'absolute',left:13,bottom:18,width:131,height:197,objectFit:'contain',filter:'drop-shadow(0 2px 2px #0005)'}}/>
  <Img src={staticFile('expressions/takosan_normal_closed.png')} style={{position:'absolute',right:11,bottom:20,width:147,height:171,objectFit:'contain',filter:'drop-shadow(0 2px 2px #0005)'}}/>
</AbsoluteFill>;
