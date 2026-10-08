import React from 'react';
import {AbsoluteFill,Audio,Img,Sequence,staticFile,useCurrentFrame,interpolate,getInputProps} from 'remotion';
import m from './edit-manifest.json';
const green='#4b8e35', purple='#9c498c', ink='#28353c';
const slides:Record<string,{chapter:string;title:string;image?:string;label:string;body:string[]}>={
 intro:{chapter:'今回のテーマ',title:'窓際社員は、なぜ\n屋外へ移動するのか',label:'窓際族物語を読み解く',body:['座席配置から考える、職場の変化。']},
 chair:{chapter:'01　入社時の支給備品',title:'アーロンチュア',image:'episode_01.png',label:'主な材質：段ボール',body:['本人の評価は「快適」。','まずは、この椅子から。']},
 movement:{chapter:'02　座席の移動過程',title:'窓際から、窓の外へ',label:'建物の境界を越える配置転換',body:['一般オフィス','窓際','ベランダ']},
 balcony:{chapter:'03　本人による環境評価',title:'寒い。だが、ビールは冷える。',image:'episode_03.png',label:'評価基準：ビールの温度',body:['冬の屋外という環境を、','冷却設備として活用。']},
 bar:{chapter:'04　環境への適応',title:'ベランダで立ち飲み屋を開店',image:'episode_04.png',label:'座席から、営業拠点へ',body:['席を戻す前に、店を出す。','オフィスに新たな機能が生まれる。']},
 conclusion:{chapter:'まとめ',title:'座席の屋外移動と\n飲食店の形成',label:'観察された流れ',body:['座席移動　→　屋外勤務　→　開店','出典：原作漫画 第1〜4話']}
};
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);
 const previous=[...m.dialogue].reverse().find(d=>f>=d.startFrame);
 const scene=previous?.scene??'intro';const slide=slides[scene];const credits=f>=m.creditsStartFrame;
 const titleTransition=f>=m.dialogue[3].startFrame+m.dialogue[3].durationInFrames+9&&f<m.mainStartFrame;
 const start=m.dialogue.find(d=>d.scene===scene)?.startFrame??0;
 const entry=interpolate(f-start,[0,9],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{background:'#f3f0e6',fontFamily:'"Hiragino Sans", "Noto Sans JP", sans-serif',color:ink}}>
  <AbsoluteFill style={{backgroundImage:'linear-gradient(#d8ddd733 1px,transparent 1px),linear-gradient(90deg,#d8ddd733 1px,transparent 1px)',backgroundSize:'32px 32px'}}/>
  <div style={{position:'absolute',left:0,right:0,top:0,height:70,background:'#274c43',color:'white',display:'flex',alignItems:'center',justifyContent:'space-between',padding:'0 48px',fontSize:23,fontWeight:600}}><span>ずんだもんと学ぶ 窓際族物語</span><span style={{fontSize:17,fontWeight:400}}>原作漫画 解説 ｜ 検証版</span></div>
  {m.dialogue.map((d,i)=><Sequence key={i} from={d.startFrame} durationInFrames={d.durationInFrames}><Audio src={staticFile(d.audio)}/></Sequence>)}
  <Sequence durationInFrames={m.mainStartFrame}><Audio src={staticFile('intro.mp3')} volume={frame=>.12*interpolate(frame,[0,15,m.mainStartFrame-24,m.mainStartFrame],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/></Sequence>
  {!getInputProps().omitMainMusic&&<Sequence from={m.mainStartFrame}><Audio src={staticFile('main.wav')} volume={frame=>.105*interpolate(frame,[0,18,m.composition.durationInFrames-m.mainStartFrame-30,m.composition.durationInFrames-m.mainStartFrame],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/></Sequence>}
  {!credits&&<>
   <div style={{position:'absolute',left:224,top:94,width:832,height:438,background:'#fffef9',border:'2px solid #cfd5cb',boxShadow:'0 5px 0 #d7ddd3',borderRadius:7,overflow:'hidden'}}>
    <div style={{height:43,padding:'9px 22px',boxSizing:'border-box',borderBottom:'1px solid #dce1d7',fontSize:19,color:'#567063',fontWeight:600}}>{titleTransition?'本編':slide.chapter}</div>
    <div style={{opacity:entry,padding:'15px 22px'}}>
     <div style={{fontWeight:700,fontSize:scene==='intro'||scene==='conclusion'?41:29,lineHeight:1.4,whiteSpace:'pre-line',textAlign:scene==='intro'||scene==='conclusion'?'center':'left',marginTop:scene==='intro'?36:0}}>{slide.title}</div>
     {slide.image?<div style={{display:'flex',gap:23,marginTop:10,alignItems:'center'}}>
      <Img src={staticFile(slide.image)} style={{width:288,height:288,objectFit:'contain',border:'1px solid #d1d1c7'}}/>
      <div style={{flex:1,fontSize:21,lineHeight:1.7}}><div style={{fontSize:25,fontWeight:600,borderBottom:'3px solid #cad9b7',paddingBottom:10,marginBottom:18}}>{slide.label}</div>{slide.body.map(t=><div key={t}>{t}</div>)}<div style={{fontSize:15,color:'#7b8179',marginTop:23}}>資料：窓際族物語 原作漫画</div></div>
     </div>:scene==='movement'?<><div style={{display:'flex',alignItems:'center',justifyContent:'center',marginTop:58,gap:14}}>{slide.body.map((t,i)=><React.Fragment key={t}>{i>0&&<span style={{fontSize:30,color:'#849384'}}>→</span>}<div style={{padding:'22px 16px',border:'2px solid '+(i===2?'#b8664c':'#9cafa1'),borderRadius:6,background:i===2?'#fff0df':'#f1f5ef',fontSize:25,fontWeight:600}}>{t}</div></React.Fragment>)}</div><div style={{textAlign:'center',fontSize:22,marginTop:38}}>{slide.label}</div></>:<div style={{textAlign:'center',marginTop:34}}><div style={{fontSize:24,color:'#557447',fontWeight:600,marginBottom:22}}>{slide.label}</div>{slide.body.map(t=><div key={t} style={{fontSize:22,lineHeight:1.8}}>{t}</div>)}</div>}
    </div>
   </div>
   {(['zunda','metan'] as const).map((who,i)=>{
    const speaking=active?.who===who;const j=active?f-active.startFrame:0;const open=speaking&&(active?.envelope[j]??0)>.023;
    const blink=(f+(i?49:0))%127<4;const mood=blink?'blink':speaking&&'mood' in active&&active.mood==='surprise'?'surprise':'normal';
    return <div key={who} style={{position:'absolute',left:i?1056:0,top:260,width:224,transform:`translateY(${speaking?-2:0}px)`}}><Img src={staticFile(`${who}_${mood}_${Number(open)}.png`)} style={{width:'100%',filter:'drop-shadow(0px 3px 1px #0002)'}}/></div>
   })}
   <div style={{position:'absolute',left:65,right:65,top:559,height:121,background:'#fffefa',border:`3px solid ${active?.who==='zunda'?green:purple}`,borderRadius:10,boxShadow:'0 3px 0 #0001',display:'flex',alignItems:'center',justifyContent:'center',padding:'14px 30px',boxSizing:'border-box'}}>
    <div style={{position:'absolute',left:20,top:-18,padding:'3px 17px',background:active?.who==='zunda'?green:purple,color:'white',borderRadius:5,fontSize:19}}>{active?.who==='zunda'?'ずんだもん':'四国めたん'}</div>
    <div style={{fontSize:30,fontWeight:600,lineHeight:1.5,textAlign:'center',whiteSpace:'pre-line',lineBreak:'strict',overflowWrap:'anywhere'}}>{active?.caption??(titleTransition?'窓際社員の移動過程を見ていきましょう。':'')}</div>
   </div>
  </>}
  {credits&&<div style={{position:'absolute',inset:'100px 130px 85px',background:'#fffef9',border:'2px solid #cfd5cb',borderRadius:8,padding:35,textAlign:'center'}}><div style={{fontSize:30,fontWeight:700,marginBottom:25}}>窓際族物語 解説動画・検証版</div><div style={{fontSize:23,lineHeight:1.9}}>音声：VOICEVOX:ずんだもん ／ VOICEVOX:四国めたん<br/>立ち絵：坂本アヒル 様<br/>導入BGM：昼下がり気分 ／ KK<br/>{getInputProps().omitMainMusic ? "本編BGM：音源受領後に追加" : "本編BGM：ほのぼのワルツ【リコーダー】／ エクシエ"}<br/>原作：窓際族物語<br/><span style={{fontSize:18}}>本作は架空の企業・出来事を扱うフィクションです。</span></div></div>}
  <div style={{position:'absolute',bottom:9,left:48,fontSize:13,color:'#687367'}}>窓際族物語の漫画世界を解説するフィクションです。</div>
  <div style={{position:'absolute',bottom:0,left:0,height:4,width:`${f/m.composition.durationInFrames*100}%`,background:'#6f9761'}}/>
 </AbsoluteFill>
};
