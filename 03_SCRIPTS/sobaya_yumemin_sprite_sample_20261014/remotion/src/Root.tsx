import React from 'react';
import {ExpressionSample} from './ExpressionSample';
import expressionData from './manifest_expressions.json';
import {AbsoluteFill,Audio,Composition,Img,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import data from './edit-manifest.json';
import hau from './manifest_hau.json';
import himari from './manifest_himari.json';
import sayo from './manifest_sayo.json';
import {memberCaptionStyle} from './member-colors';
const Sample:React.FC<{data:typeof data; voiceLabel:string}>=({data,voiceLabel})=>{
 const f=useCurrentFrame(); const line=data.lines.find(l=>f>=l.start&&f<l.start+l.frames+12);
 const last=[...data.lines].reverse().find(l=>f>=l.start); const pose=last?.pose??'normal';
 const local=line?f-line.start:0; const speaking=!!line&&local<line.frames;
 const energy=speaking?(line.energy[Math.floor(local)]??0):0;
 const sy=speaking&&line?.who==='sobaya'?-energy*3:0;
 const yy=Math.sin(f/22)*4-(speaking&&line?.who==='yumemin'?energy*8:0);
 const fade=interpolate(f,[0,10,data.composition.durationInFrames-15,data.composition.durationInFrames-1],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{background:'#fff',fontFamily:'Hiragino Sans, sans-serif'}}><AbsoluteFill style={{opacity:fade}}>
 <div style={{position:'absolute',left:70,top:38,color:'#667078',fontSize:22,letterSpacing:2}}>そば屋 × ゆめみん</div>
 <div style={{position:'absolute',right:70,top:42,color:'#889096',fontSize:16}}>{voiceLabel || "立ち絵サンプル"}</div>
 <div style={{position:'absolute',left:84,top:83,width:485,height:484,transform:`translateY(${sy}px) scaleX(-1)`}}>
 <Img src={staticFile(`sobaya_${pose}.png`)} style={{width:'100%',height:'100%',objectFit:'contain',objectPosition:'center bottom'}}/>
 </div>
 <div style={{position:'absolute',right:110,top:214,width:360,height:340,transform:`translateY(${yy}px) rotate(${speaking&&line?.who==='yumemin'?Math.sin(f/7)*1.1:0}deg)`}}>
 <Img src={staticFile('yumemin.png')} style={{width:'100%',height:'100%',objectFit:'contain'}}/>
 </div>
 <div style={{position:'absolute',left:0,right:0,top:592,textAlign:'center',padding:'0 60px',fontSize:34,fontWeight:700,lineHeight:1.45,...memberCaptionStyle(line?.who==='sobaya'?'そば屋':'ゆめみん')}}>{line?.text??''}</div>
 </AbsoluteFill>{data.lines.map(l=><Sequence key={l.audio} from={l.start} durationInFrames={l.frames}><Audio src={staticFile(l.audio)}/></Sequence>)}</AbsoluteFill>;
};
export const Root:React.FC=()=> <>
 <Composition id="Expressive" component={ExpressionSample} durationInFrames={expressionData.composition.durationInFrames} fps={30} width={1280} height={720}/>
 <Composition id="Sample" component={Sample} defaultProps={{data,voiceLabel:''}} durationInFrames={data.composition.durationInFrames} fps={30} width={1280} height={720}/>
 {([{id:'Hau',manifest:hau,label:'ゆめみん：雨晴はう'},{id:'Himari',manifest:himari,label:'ゆめみん：冥鳴ひまり'},{id:'Sayo',manifest:sayo,label:'ゆめみん：小夜/SAYO'}]).map(v=><Composition key={v.id} id={v.id} component={Sample} defaultProps={{data:v.manifest,voiceLabel:v.label}} durationInFrames={v.manifest.composition.durationInFrames} fps={30} width={1280} height={720}/>)}
 </>;
