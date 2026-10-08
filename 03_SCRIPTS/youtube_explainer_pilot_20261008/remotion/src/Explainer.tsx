import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame,interpolate,getInputProps} from 'remotion';
import m from './edit-manifest.json';
const images:Record<string,string>={intro:'episode_02.png',chair:'episode_01.png',movement:'episode_02.png',balcony:'episode_03.png',bar:'episode_04.png',conclusion:'episode_04.png'};
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();
 const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);
 const previous=[...m.dialogue].reverse().find(d=>f>=d.startFrame);
 const scene=previous?.scene??'intro';
 const credits=f>=m.creditsStartFrame;
 // Switch the source panel when the narration reaches the balcony.
 const sceneImage=scene==='movement'&&f>=m.dialogue[7].startFrame+90?'episode_03.png':images[scene];
 return <AbsoluteFill style={{background:'#f3f0e6',fontFamily:'"Hiragino Sans", "Noto Sans JP", sans-serif',color:'#28353c'}}>
  {m.dialogue.map((d,i)=><Sequence key={i} from={d.startFrame} durationInFrames={d.durationInFrames}><Audio src={staticFile(d.audio)}/></Sequence>)}
  <Sequence durationInFrames={m.mainStartFrame}><Audio src={staticFile('intro.mp3')} volume={frame=>.12*interpolate(frame,[0,15,m.mainStartFrame-24,m.mainStartFrame],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/></Sequence>
  {!getInputProps().omitMainMusic&&<Sequence from={m.mainStartFrame}><Audio src={staticFile('main.wav')} volume={frame=>.105*interpolate(frame,[0,18,m.composition.durationInFrames-m.mainStartFrame-30,m.composition.durationInFrames-m.mainStartFrame],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/></Sequence>}
  {!credits&&<>
   <Img src={staticFile(sceneImage)} style={{position:'absolute',left:380,top:30,width:520,height:520,objectFit:'contain'}}/>
   {(['zunda','metan'] as const).map((who,i)=>{
    const speaking=active?.who===who;
    const j=active?f-active.startFrame:0;
    const open=speaking&&(active?.envelope[j]??0)>.023;
    const blink=(f+(i?49:0))%127<4;
    const mood=blink?'blink':speaking&&'mood' in active&&active.mood==='surprise'?'surprise':'normal';
    return <Img key={who} src={staticFile(`${who}_${mood}_${Number(open)}.png`)} style={{position:'absolute',left:i?940:20,bottom:0,width:320}}/>;
   })}
   {active&&<div style={{position:'absolute',left:80,right:80,bottom:27,minHeight:106,display:'flex',alignItems:'center',justifyContent:'center'}}>
    <div style={{fontSize:33,fontWeight:800,lineHeight:1.5,textAlign:'center',whiteSpace:'pre-line',color:active.who==='zunda'?'#347526':'#8d397c',WebkitTextStroke:'7px #fff',paintOrder:'stroke fill',textShadow:'0 2px 3px #0003'}}>{active.caption}</div>
   </div>}
  </>}
  {credits&&<div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',fontSize:23,lineHeight:2}}><div>音声：VOICEVOX:ずんだもん ／ VOICEVOX:四国めたん<br/>立ち絵：坂本アヒル 様<br/>導入BGM：昼下がり気分 ／ KK<br/>{getInputProps().omitMainMusic?'本編BGM：音源受領後に追加':'本編BGM：ほのぼのワルツ【リコーダー】／ エクシエ'}<br/>原作：窓際族物語</div></div>}
 </AbsoluteFill>;
};
