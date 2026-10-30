import React from 'react';
import {AbsoluteFill,Composition,OffthreadVideo,Sequence,staticFile,useCurrentFrame} from 'remotion';
import m from './edit-manifest.json';
const Video:React.FC=()=>{const f=useCurrentFrame();const flash=m.segments[2].startFrame;const end=m.composition.durationInFrames;return <AbsoluteFill style={{backgroundColor:'#15130f'}}>
 {m.segments.map(s=><Sequence key={s.id} from={s.startFrame} durationInFrames={s.durationInFrames}><AbsoluteFill style={{justifyContent:'center'}}><OffthreadVideo src={staticFile(s.id+'_720p.mp4')} muted style={{width:1280,height:720,objectFit:'contain'}}/></AbsoluteFill></Sequence>)}
 {f>=flash&&f<flash+72&&<div style={{position:'absolute',left:52,top:38,color:'#fff',fontFamily:'Hiragino Sans',fontWeight:800,fontSize:34,textShadow:'0 2px 5px #000',background:'#0007',padding:'9px 20px',borderRadius:8}}>去年のお正月</div>}
 {f>=end-60&&<div style={{position:'absolute',left:0,right:0,bottom:22,textAlign:'center',color:'#fff7d8',fontFamily:'Hiragino Mincho ProN',fontWeight:800,fontSize:46,textShadow:'0 3px 6px #522400, 0 0 12px #522400'}}>今年もよろしくお願いします</div>}
 </AbsoluteFill>};
export const Root:React.FC=()=> <Composition id="NewYear" component={Video} {...m.composition}/>;
