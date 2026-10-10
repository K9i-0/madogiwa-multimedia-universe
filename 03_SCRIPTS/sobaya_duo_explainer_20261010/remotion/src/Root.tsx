import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import original from './edit-manifest.json';
import voicevox from './edit-manifest-voicevox.json';
import {Sprite,moods,Mood,Who} from './Sprite';
const Center:React.FC<{scene:string}>=({scene})=>{
 const title:Record<string,string>={intro:'そば屋って、どんな人？',profile:'見た目は、かなり強そう',kind:'怖そう。でも、優しい。',chair:'愛用品はアーロンチュア',balcony:'窓際の、その外へ',positive:'「ビールが冷えたまま」',bar:'ベランダで、立ち飲み処',fall:'お店が、ベランダごと落下',rebuild:'片付けて、もう一度つくる',campaign:'やめさん確保で……',escape:'壁を破って、脱走',summary:'怪力と、前向きさと、ビール'};
 const file:Record<string,string>={chair:'episode_01.png',balcony:'episode_03.png',positive:'episode_03.png',bar:'episode_04.png',fall:'episode_06.jpeg',rebuild:'episode_08.png',campaign:'episode_05.png',escape:'episode_12.png'};
 return <div style={{position:'absolute',left:350,top:35,width:580,height:550,display:'flex',alignItems:'center',flexDirection:'column'}}>
  <div style={{fontSize:27,fontWeight:600,marginBottom:17,lineHeight:1.4,textAlign:'center'}}>{title[scene]}</div>
  {file[scene]?<><Img src={staticFile(file[scene])} style={{height:445,maxWidth:550,objectFit:'contain',borderRadius:4}}/><div style={{fontSize:15,color:'#86827a',marginTop:10}}>原作「窓際族物語」</div></>:<>
   <div style={{position:'relative',width:200,height:420,overflow:'hidden',borderRadius:6}}><Img src={staticFile('sobaya_sheet.png')} style={{position:'absolute',width:900,maxWidth:'none',left:0,top:-58}}/></div>
   {scene==='profile'?<div style={{fontSize:24,marginTop:14}}>41歳　180cm　100kg</div>:scene==='summary'?<div style={{fontSize:22,marginTop:14}}>窓際を、自分の居場所に。</div>:scene==='kind'?<div style={{fontSize:23,marginTop:14}}>乾杯から、仲良くなれる。</div>:<div style={{fontSize:22,marginTop:14}}>たこさん × やめ太郎</div>}
  </>}
 </div>;
};
const Sobaya:React.FC<{m:typeof original;credit:string}>=({m,credit})=>{
 const f=useCurrentFrame();const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);const latest=[...m.dialogue].reverse().find(d=>f>=d.startFrame);
 const end=f>=m.composition.durationInFrames-75;
 return <AbsoluteFill style={{background:'#f3f0e8',fontFamily:'"Hiragino Sans","Noto Sans JP",sans-serif',color:'#34383e'}}>
  {m.dialogue.map((d,i)=><Sequence key={i} from={d.startFrame} durationInFrames={d.durationInFrames}><Audio src={staticFile(d.audio)}/></Sequence>)}
  <Center scene={latest?.scene??'intro'}/>
  {(['takosan','yametaro'] as Who[]).map((who,i)=>{
   const speaking=active?.who===who;const own=[...m.dialogue].reverse().find(d=>d.who===who&&f>=d.startFrame);const mood=(own?.mood??'normal') as Mood;const local=speaking?f-active!.startFrame:0;
   const open=speaking&&(active?.envelope[Math.floor(local/2)*2]??0)>.018;
   const bob=speaking?Math.sin(local*.20)*1.4:0;const recoil=speaking&&mood==='surprise'&&local<16?Math.sin(local/16*Math.PI)*(i?-1.5:1.5):0;
   const w=i?320:370;const h=w*(i?1536/1024:1351/1164);
   return <div key={who} style={{position:'absolute',left:i?955:-10,bottom:102,width:w,height:h,transform:`translateY(${bob}px) rotate(${recoil}deg)`,transformOrigin:'50% 88%'}}><Sprite who={who} mood={mood} open={open} blink={!i&&(f+17)%137<4} mirror={!i}/></div>;
  })}
  {active&&<div style={{position:'absolute',left:64,right:64,bottom:27,minHeight:87,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',fontSize:29,fontWeight:600,lineHeight:1.5,whiteSpace:'pre-line',color:active.who==='takosan'?'#39444b':'#725198',WebkitTextStroke:'4px #fff',paintOrder:'stroke fill'}}>{active.caption}</div>}
  {end&&<div style={{position:'absolute',left:360,right:360,bottom:25,textAlign:'center',fontSize:15,color:'#858077',opacity:interpolate(f,[m.composition.durationInFrames-75,m.composition.durationInFrames-60],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>原作・キャラクター：窓際族物語<br/>音声：{credit} ／ 編集：Remotion</div>}
 </AbsoluteFill>;
};
const Sheet:React.FC<{who:Who}>=({who})=>{
 const f=useCurrentFrame();return <AbsoluteFill style={{background:'transparent'}}><Sprite who={who} mood={moods[Math.floor(f/2)%8]} open={f%2===1}/></AbsoluteFill>;
};
export const Root:React.FC=()=> <>
 <Composition id="Sobaya" component={Sobaya} defaultProps={{m:original,credit:"Irodori-TTS"}} {...original.composition}/>
 <Composition id="SobayaVoicevox" component={Sobaya} defaultProps={{m:voicevox as unknown as typeof original,credit:"VOICEVOX:Voidoll / Irodori-TTS"}} {...voicevox.composition}/>
 <Composition id="TakosanSprites" component={()=> <Sheet who="takosan"/>} width={1164} height={1351} fps={1} durationInFrames={16}/>
 <Composition id="YametaroSprites" component={()=> <Sheet who="yametaro"/>} width={1024} height={1536} fps={1} durationInFrames={16}/>
</>;
