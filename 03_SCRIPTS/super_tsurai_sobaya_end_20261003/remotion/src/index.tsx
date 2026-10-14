import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,OffthreadVideo,Sequence,registerRoot,staticFile,useCurrentFrame,interpolate} from 'remotion';
const End=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{background:'#222'}}>
<OffthreadVideo src={staticFile('wan_720p.mp4')} muted style={{width:'100%',height:'100%'}}/>
<div style={{position:'absolute',right:0,top:0,bottom:0,width:620,background:'linear-gradient(90deg,transparent,rgba(0,0,0,.18))'}}/>
<Img src={staticFile('title_meme.png')} style={{position:'absolute',right:24,top:90,width:390,opacity:interpolate(f,[14,23],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
<Sequence from={6}><Audio src={staticFile('product_call.wav')}/></Sequence>
</AbsoluteFill>};
registerRoot(()=> <Composition id="SobayaEnd" component={End} width={1280} height={720} fps={30} durationInFrames={90}/>);
