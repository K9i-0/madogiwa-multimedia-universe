import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,registerRoot,staticFile,useCurrentFrame,interpolate} from 'remotion';
const End=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{background:'#000'}}><OffthreadVideo src={staticFile('ng3.mp4')} muted style={{width:1280,height:720}}/><Img src={staticFile('title.png')} style={{position:'absolute',left:55,bottom:35,width:350,filter:'drop-shadow(0 3px 8px #000a)',opacity:interpolate(f,[6,15],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/></AbsoluteFill>};
registerRoot(()=> <Composition id="Ng3End" component={End} width={1280} height={720} fps={30} durationInFrames={90}/>);
