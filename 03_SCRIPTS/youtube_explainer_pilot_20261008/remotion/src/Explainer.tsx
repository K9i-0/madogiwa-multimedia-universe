import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame,interpolate,getInputProps} from 'remotion';
import m from './edit-manifest.json';
// Central content is selected by the explanation, not by a fixed image template.
const SceneContent:React.FC<{scene:string;frame:number}>=({scene,frame})=>{
 const picture=(name:string,size=460)=><Img src={staticFile(name)} style={{width:size,height:size,objectFit:'contain'}}/>;
 const stage:React.CSSProperties={position:'absolute',left:345,top:35,width:590,height:515,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',textAlign:'center'};
 if(scene==='intro')return <div style={stage}>
  <div style={{fontSize:23,color:'#687367',marginBottom:28}}>窓際族物語</div>
  <div style={{fontSize:45,fontWeight:700,lineHeight:1.65}}>窓際社員は、なぜ<br/>屋外へ移動するのか</div>
  {frame>=m.dialogue[2].startFrame&&<div style={{fontSize:26,marginTop:35,color:'#8d397c'}}>※ 移動先には、建物の外側を含む</div>}
 </div>;
 if(scene==='movement'){
  const outside=frame>=m.dialogue[7].startFrame+90;
  return <div style={stage}>
   <div style={{fontSize:31,fontWeight:600,marginBottom:30}}>社員の座席の移動</div>
   <div style={{display:'flex',alignItems:'center',gap:14,fontSize:26}}>
    <span>オフィス</span><span style={{color:'#899187'}}>→</span><span>窓際</span><span style={{color:'#899187'}}>→</span><span style={{color:outside?'#8d397c':'#9ba198',fontWeight:outside?700:400}}>ベランダ</span>
   </div>
   <div style={{marginTop:24}}>{picture(outside?'episode_03.png':'episode_02.png',300)}</div>
  </div>;
 }
 if(scene==='conclusion')return <div style={stage}>
  <div style={{fontSize:24,color:'#687367',marginBottom:28}}>今回の観察結果</div>
  <div style={{fontSize:37,fontWeight:700,lineHeight:1.7}}>座席を屋外へ移すと、<br/>飲食店ができる。</div>
  <div style={{display:'flex',alignItems:'center',gap:28,marginTop:28}}>{picture('episode_03.png',155)}<span style={{fontSize:30,color:'#899187'}}>→</span>{picture('episode_04.png',155)}</div>
 </div>;
 const name=scene==='chair'?'episode_01.png':scene==='balcony'?'episode_03.png':'episode_04.png';
 return <div style={stage}>{picture(name,scene==='chair'?450:510)}
  {scene==='chair'&&frame>=m.dialogue[5].startFrame&&<div style={{fontSize:29,fontWeight:600,marginTop:16}}>アーロンチュア <span style={{color:'#687367',fontSize:25}}>／ 段ボール製</span></div>}
 </div>;
};
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();
 const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);
 const previous=[...m.dialogue].reverse().find(d=>f>=d.startFrame);
 const scene=previous?.scene??'intro';
 const credits=f>=m.creditsStartFrame;
 return <AbsoluteFill style={{background:'#f3f0e6',fontFamily:'"Hiragino Sans", "Noto Sans JP", sans-serif',color:'#28353c'}}>
  {m.dialogue.map((d,i)=><Sequence key={i} from={d.startFrame} durationInFrames={d.durationInFrames}><Audio src={staticFile(d.audio)}/></Sequence>)}
  <Sequence durationInFrames={m.mainStartFrame}><Audio src={staticFile('intro.mp3')} volume={frame=>.12*interpolate(frame,[0,15,m.mainStartFrame-24,m.mainStartFrame],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/></Sequence>
  {!getInputProps().omitMainMusic&&<Sequence from={m.mainStartFrame}><Audio src={staticFile('main.wav')} volume={frame=>.105*interpolate(frame,[0,18,m.composition.durationInFrames-m.mainStartFrame-30,m.composition.durationInFrames-m.mainStartFrame],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/></Sequence>}
  {!credits&&<>
   <SceneContent scene={scene} frame={f}/>
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
