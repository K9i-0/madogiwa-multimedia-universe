import React from 'react';
import {AbsoluteFill,Composition,Img,registerRoot} from 'remotion';
const Thumbnail=({game,zunda,overlay=false}:{game:string,zunda:string,overlay?:boolean})=><AbsoluteFill style={{background:overlay?'transparent':'#102335',fontFamily:'"Hiragino Sans",sans-serif',overflow:'hidden'}}>
 {!overlay&&<Img src={game} style={{position:'absolute',left:150,top:201,width:1130,height:519}}/>}
 <div style={{position:'absolute',left:0,top:200,width:400,height:520,background:'linear-gradient(90deg,#102335 0%,rgba(16,35,53,.85) 25%,transparent 100%)'}}/>
 <div style={{position:'absolute',inset:'0 0 auto',height:200,background:'#102335',borderBottom:'5px solid #51d3ef'}}/>
 <div style={{position:'absolute',top:18,left:50,color:'#70def3',fontSize:32,fontWeight:800,letterSpacing:1}}>Flutter Scene <span style={{color:'#93a9b9',padding:'0 14px'}}>×</span><span style={{color:'#fff'}}>3Dゲーム</span></div>
 <div style={{position:'absolute',left:40,top:58,fontSize:116,fontWeight:900,letterSpacing:-5,lineHeight:1.1,whiteSpace:'nowrap',color:'white',textShadow:'0 6px 0 #07131e'}}>これ、<span style={{color:'#ffdc5c'}}>Flutter!?</span></div>
 <Img src={zunda} style={{position:'absolute',left:0,top:252,width:459,height:477,objectFit:'contain',filter:'drop-shadow(0 8px 12px rgba(0,0,0,.4))'}}/>
</AbsoluteFill>;
registerRoot(()=> <Composition id="Thumbnail" component={Thumbnail as any} width={1280} height={720} fps={30} durationInFrames={1} defaultProps={{game:'',zunda:''}}/>);
