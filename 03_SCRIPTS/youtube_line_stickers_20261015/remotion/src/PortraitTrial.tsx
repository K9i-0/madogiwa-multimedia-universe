import React from 'react';
import {AbsoluteFill,Freeze,useCurrentFrame,interpolate} from 'remotion';
import {Explainer} from './Explainer';
export const PortraitTrial:React.FC=()=>{
 const f=useCurrentFrame();
 return <AbsoluteFill><Freeze frame={Math.min(f,1902)}><Explainer portrait silentPreview/></Freeze>
 {f>=1903&&<div style={{position:'absolute',left:20,right:20,top:1030,height:230,background:'#102c24',display:'flex',alignItems:'center',justifyContent:'center',fontFamily:'"Hiragino Sans",sans-serif',fontSize:58,fontWeight:700,color:'#fff2d4',opacity:interpolate(f,[1903,1909],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>続きは本編で</div>}
 </AbsoluteFill>;
};
