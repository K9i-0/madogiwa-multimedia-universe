import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,Sequence,staticFile,useCurrentFrame} from 'remotion';
import m from './edit-manifest.json';
const Sprite:React.FC<{who:'takosan'|'yametaro';speaking:boolean;open:boolean;happy:boolean;surprise:boolean;local:number}>=({who,speaking,open,happy,surprise,local})=>{
 const f=useCurrentFrame();const tako=who==='takosan';const w=tako?1164:1024;const h=tako?1351:1536;
 const blink=tako&&((f+23)%119<4||happy);
 const bob=speaking?Math.sin(local*.19)*1.6:0;
 const recoil=surprise&&local<18?Math.sin(local/18*Math.PI)*-2:0;
 const imageStyle:React.CSSProperties={position:'absolute',inset:0,width:'100%',height:'100%'};
 const patch=(name:string,mask:string)=><Img src={staticFile(`${who}_${name}.png`)} style={{...imageStyle,maskImage:mask,WebkitMaskImage:mask}}/>;
 const mouthMask=tako?'radial-gradient(ellipse 4.4% 2.7% at 38% 43.3%, black 75%, transparent 100%)':'radial-gradient(ellipse 5.3% 2.5% at 36.5% 47.2%, black 78%, transparent 100%)';
 return <div style={{position:'absolute',left:tako?5:895,top:tako?95:82,width:tako?460:360,height:(tako?460:360)*h/w,transform:`translateY(${bob}px) rotate(${recoil}deg)`,transformOrigin:'50% 85%'}}>
  <div style={{position:'absolute',inset:0,transform:tako?'scaleX(-1)':undefined}}>
   <Img src={staticFile(`${who}_base.png`)} style={imageStyle}/>
   {blink&&patch('blink','radial-gradient(ellipse 5% 5% at 32.8% 37.6%,black 75%,transparent 100%),radial-gradient(ellipse 5.6% 5% at 49% 37.7%,black 75%,transparent 100%)')}
   {open?patch('open',mouthMask):surprise?patch('surprise',mouthMask):null}
  </div>
 </div>
};
const Duo:React.FC=()=>{
 const f=useCurrentFrame(); const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);
 const idx=active?m.dialogue.indexOf(active):-1;const previous=[...m.dialogue].reverse().find(d=>f>=d.startFrame); const stage=previous?m.dialogue.indexOf(previous):0;
 const titles=['立ち絵で解説してみる','立ち絵で解説してみる','口パク ＋ 表情','口パク ＋ 表情','動いている ≠ 進んでいる','動いている ≠ 進んでいる'];
 return <AbsoluteFill style={{background:'#f3f0e8',fontFamily:'"Hiragino Sans",sans-serif',color:'#34383e'}}>
  {m.dialogue.map((d,i)=><Sequence key={i} from={d.startFrame} durationInFrames={d.durationInFrames}><Audio src={staticFile(d.audio)}/></Sequence>)}
  <div style={{position:'absolute',left:455,right:440,top:190,textAlign:'center'}}><div style={{fontSize:18,color:'#929088',letterSpacing:3,marginBottom:24}}>窓際族物語</div><div style={{fontSize:34,fontWeight:600,lineHeight:1.7}}>{titles[stage]}</div><div style={{fontSize:19,color:'#8d8a84',marginTop:25}}>たこさん × やめ太郎</div></div>
  {(['takosan','yametaro'] as const).map(who=>{
   const speaking=active?.who===who; const local=active?f-active.startFrame:0;const open=speaking&&(active?.envelope[Math.floor(local/2)*2]??0)>.018;
   return <Sprite key={who} who={who} speaking={speaking} open={open} local={local} happy={who==='takosan'&&idx===2&&local>40} surprise={who==='yametaro'&&((speaking&&active?.mood==='surprise')||(idx===4&&local>65))}/>;
  })}
  {active&&<div style={{position:'absolute',left:75,right:75,bottom:56,textAlign:'center',fontSize:32,fontWeight:600,lineHeight:1.6,color:active.who==='takosan'?'#41494d':'#705299',WebkitTextStroke:'4px #fff',paintOrder:'stroke fill'}}>{active.text}</div>}
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="Duo" component={Duo} {...m.composition}/>;
