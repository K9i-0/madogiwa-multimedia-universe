import React from 'react';
import {AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, interpolate} from 'remotion';
import type {EditManifest} from './types';
export const EditComposition: React.FC<{manifest: EditManifest}> = ({manifest}) => {
 const f=useCurrentFrame();
 const c=manifest.captions.find(x=>f>=x.startFrame && f<x.endFrame);
 const opacity=c?Math.min(interpolate(f,[c.startFrame,c.startFrame+4],[0,1],{extrapolateRight:'clamp'}),interpolate(f,[c.endFrame-4,c.endFrame],[1,0],{extrapolateLeft:'clamp'})):0;
 return <AbsoluteFill style={{backgroundColor:'#000'}}>
  <OffthreadVideo src={staticFile(manifest.inputVideo)} style={{width:'100%',height:'100%'}} muted />
  {c && <AbsoluteFill style={{justifyContent:'flex-end',alignItems:'center',paddingBottom:63,opacity}}>
   <div style={{position:'absolute',bottom:0,width:'100%',height:185,background:'linear-gradient(transparent,rgba(2,7,22,.67))'}} />
   <div style={{position:'relative',textAlign:'center',maxWidth:1120,fontFamily:'"Hiragino Sans",sans-serif',fontSize:43,fontWeight:600,lineHeight:1.4,letterSpacing:1.4,color:'#fff',whiteSpace:'pre-line',WebkitTextStroke:'1.5px #102331',paintOrder:'stroke fill',textShadow:'0 2px 3px #000, 0 0 12px #41dced, 0 0 26px #1695c488'}}>{c.text}</div>
   <div style={{position:'relative',width:180,height:2,marginTop:13,background:'linear-gradient(90deg,transparent,#66edff,transparent)',boxShadow:'0 0 9px #4de9ff'}} />
  </AbsoluteFill>}
 </AbsoluteFill>;
};
