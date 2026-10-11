import React from 'react';
import {AbsoluteFill,Composition,Img,OffthreadVideo,Sequence,registerRoot,staticFile,useCurrentFrame,interpolate} from 'remotion';
import m from './shorts-clean-manifest.json';
const Shot:React.FC<{shot:typeof m.shots[number];last:boolean}>=({shot:s,last})=>{
 const f=useCurrentFrame();
 const scale=last?1.85:s.kind==='image'&&s.file.endsWith('_v9.png')?interpolate(f,[0,s.duration-1],[1,1.045],{extrapolateRight:'clamp'}):1;
 const style:React.CSSProperties={width:'100%',height:'100%',objectFit:'cover',transform:`scale(${scale})`,transformOrigin:last?'48% 53%':'50% 50%',filter:'saturate(.88) contrast(1.035) brightness(.98)'};
 return <AbsoluteFill style={{overflow:'hidden'}}>{s.kind==='video'?<OffthreadVideo src={staticFile(s.file)} startFrom={s.sourceStart} muted style={style}/>:<Img src={staticFile(s.file)} style={style}/>}</AbsoluteFill>;
};
const Clean:React.FC=()=> <AbsoluteFill style={{background:'#000'}}>{m.shots.map((s,i)=><Sequence key={i} from={s.from} durationInFrames={s.duration}><Shot shot={s} last={i===m.shots.length-1}/></Sequence>)}<AbsoluteFill style={{background:'rgba(22,44,72,.055)',mixBlendMode:'color'}}/><AbsoluteFill style={{background:'radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.16) 100%)'}}/></AbsoluteFill>;
registerRoot(()=> <Composition id="DetectiveShortsClean" component={Clean} width={1280} height={720} fps={30} durationInFrames={m.durationInFrames}/>);
