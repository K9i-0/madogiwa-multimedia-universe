import React from 'react';
import {AbsoluteFill} from 'remotion';
// Deterministic tape wear: sparse tracking slips, fine noise and head-switching band.
export const tapeSlip=(f:number)=>[3,4,208,209,211,417,418,537].includes(f);
export const TapeWear:React.FC<{frame:number;duration:number}>=({frame:f,duration})=>{
 const slip=tapeSlip(f);const tail=Math.min(1,(duration-f)/36);const y=(f*5.7+41)%720;
 return <AbsoluteFill style={{pointerEvents:'none',opacity:tail,overflow:'hidden'}}>
 <svg width="0" height="0"><defs><filter id="tape-warp"><feTurbulence type="fractalNoise" baseFrequency="0 .012" numOctaves="1" seed={Math.floor(f/2)%31} result="warp"/><feDisplacementMap in="SourceGraphic" in2="warp" scale={slip?19:1.8} xChannelSelector="R" yChannelSelector="G"/></filter></defs></svg>
 <svg width="1280" height="720" style={{position:'absolute',opacity:slip?.19:.065,mixBlendMode:'screen'}}><filter id="tape-grain"><feTurbulence type="fractalNoise" baseFrequency=".78 .42" numOctaves="1" seed={f%97+1}/><feColorMatrix type="saturate" values="0"/></filter><rect width="100%" height="100%" filter="url(#tape-grain)"/></svg>
 <AbsoluteFill style={{background:'repeating-linear-gradient(0deg, transparent 0px, transparent 2px, #0005 3px, transparent 4px)',opacity:.42}}/>
 <div style={{position:'absolute',left:0,right:0,top:y,height:slip?34:12,background:'linear-gradient(transparent,#b8c6bb,transparent)',opacity:slip?.20:.035}}/>
 <div style={{position:'absolute',left:0,right:0,bottom:10+(f%5),height:slip?19:3,background:'repeating-linear-gradient(90deg,#ddd9 0 7px,#0006 7px 21px,transparent 21px 29px)',opacity:slip?.45:.15}}/>
 <AbsoluteFill style={{background:'radial-gradient(ellipse, transparent 48%, #0009 100%)'}}/>
 </AbsoluteFill>;
};
