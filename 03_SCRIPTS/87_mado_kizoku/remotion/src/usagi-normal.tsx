import React from 'react';
import {AbsoluteFill,Audio,Composition,OffthreadVideo,Sequence,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import './style.css';
const Film:React.FC=()=>{
 const frame=useCurrentFrame();
 return <AbsoluteFill style={{backgroundColor:'#000'}}>
  <Sequence durationInFrames={1102}><OffthreadVideo muted src={staticFile('usagi-normal/adopted_v11.mp4')} style={{width:'100%',height:'100%'}}/></Sequence>
  <Audio src={staticFile('usagi-normal/mix.wav')}/>
  {frame>=1102&&<AbsoluteFill style={{justifyContent:'center',alignItems:'center',color:'#eee',fontFamily:'"Hiragino Sans", sans-serif',textAlign:'center',lineHeight:1.65}}>
   <div style={{fontSize:24,color:'#aaa',marginBottom:18}}>MUSIC</div>
   <div style={{fontSize:32}}>Divertissement - Pizzicato (from the ballet Sylvia)</div>
   <div style={{fontSize:30,marginTop:12}}>Kevin MacLeod (incompetech.com)</div>
   <div style={{fontSize:20,marginTop:10}}>incompetech.com/music/royalty-free/index.html?isrc=USUAN1100256</div>
   <div style={{fontSize:24,marginTop:22}}>Licensed under Creative Commons: By Attribution 4.0</div>
   <div style={{fontSize:24}}>https://creativecommons.org/licenses/by/4.0/</div>
   <div style={{fontSize:22,marginTop:20,color:'#bbb'}}>編集：抜粋・音量調整・フェード</div>
   <div style={{fontSize:27,marginTop:28}}>VOICEVOX:中国うさぎ</div>
  </AbsoluteFill>}
 </AbsoluteFill>;
};
registerRoot(()=> <Composition id="MadoOjousamaUsagi" component={Film} width={1280} height={720} fps={30} durationInFrames={1162}/>);
