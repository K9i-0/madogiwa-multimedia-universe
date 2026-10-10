import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,Sequence,OffthreadVideo,staticFile,useCurrentFrame,interpolate} from 'remotion';
import m from './edit-manifest.json';
import {Sprite,Mood,Who} from './Sprite';
const titles:Record<string,string>={intro:'そば屋の奇行5選',excel:'① Excelを開いて、閉じて',catch:'② ビールだけを救う超反応',bar:'③ ベランダをバーに改装',quake:'④ ビール禁止でオフィスが揺れる',proxy:'⑤ 仮面をかぶせて代理出社',ending:'そば屋の奇行5選'};
const pictures:Record<string,string>={};
const Center:React.FC<{visual:string}>=({visual})=>{
 if(visual==='title'||visual==='summary')return <div style={{position:'absolute',left:350,top:180,width:580,textAlign:'center'}}><div style={{fontSize:24,color:'#777269',marginBottom:20}}>窓際族物語</div><div style={{fontSize:visual==='title'?72:54,fontWeight:700,lineHeight:1.45}}>そば屋の<br/><span style={{color:'#a74935'}}>奇行5選</span></div>{visual==='summary'&&<div style={{fontSize:21,marginTop:20}}>一緒に飲む分には、ええ人。</div>}</div>;
 if(visual==='profile')return <div style={{position:'absolute',left:435,top:125,width:410,textAlign:'center'}}><div style={{position:'relative',width:200,height:400,overflow:'hidden',margin:'auto'}}><Img src={staticFile('sobaya_sheet.png')} style={{position:'absolute',width:880,maxWidth:'none',left:0,top:-56}}/></div><div style={{fontSize:22,marginTop:16}}>41歳 ／ ビール好きの窓際族</div></div>;
 const comic=!!pictures[visual];return <div style={{position:'absolute',left:280,top:123,width:720,height:430,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center'}}><Img src={staticFile(pictures[visual]??visual+'.jpg')} style={{maxWidth:720,maxHeight:410,objectFit:'contain'}}/><div style={{fontSize:14,color:'#807b71',marginTop:10}}>{comic?'原作「窓際族物語」':'過去エピソードより'}</div></div>;
};
const Film:React.FC=()=>{
 const f=useCurrentFrame();const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);const spoken=[...m.dialogue].reverse().find(d=>f>=d.startFrame);const pastClip=[...m.clips].reverse().find(c=>f>=c.startFrame+c.durationInFrames);const latest=pastClip&&pastClip.startFrame>(spoken?.startFrame??0)?m.dialogue.find(d=>d.startFrame>pastClip.startFrame)??spoken:spoken;const clip=m.clips.find(c=>f>=c.startFrame&&f<c.startFrame+c.durationInFrames);const credits=f>=m.composition.durationInFrames-140;
 return <AbsoluteFill style={{background:'#f3f0e8',fontFamily:'"Hiragino Sans","Noto Sans JP",sans-serif',color:'#34383e'}}>
 <Audio src={staticFile('mixed.wav')}/>
 {clip?<><Sequence from={clip.startFrame} durationInFrames={clip.durationInFrames} style={{opacity:interpolate(f-clip.startFrame,[0,5,clip.durationInFrames-6,clip.durationInFrames-1],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}><OffthreadVideo muted src={staticFile(clip.file)} style={{width:'100%',height:'100%',objectFit:'contain',background:'#101115'}}/></Sequence><div style={{position:'absolute',top:18,left:'50%',transform:'translateX(-50%)',padding:'7px 12px',background:'#000a',color:'white',fontSize:17}}>{clip.label}</div></>:<>
 <div style={{position:'absolute',top:43,left:125,right:125,textAlign:'center',fontSize:30,fontWeight:600}}>{titles[latest?.scene??'intro']}</div>
 <Center visual={latest?.visual??'profile'}/>
 {(['takosan','yametaro'] as Who[]).map((who,i)=>{
 const speaking=active?.who===who;const own=[...m.dialogue].reverse().find(d=>d.who===who&&f>=d.startFrame);const mood=(own?.mood??'normal') as Mood;const local=speaking?f-active!.startFrame:0;
 const open=speaking&&(active?.envelope[Math.floor(local/2)*2]??0)>.018;const w=i?268:300;const h=w*(i?1536/1024:1351/1164);
 return <div key={who} style={{position:'absolute',left:i?1020:-22,bottom:118,width:w,height:h,transform:`translateY(${speaking?Math.sin(local*.2)*1.4:0}px)`}}><Sprite who={who} mood={mood} open={open} blink={!i&&(f+17)%137<4} mirror={!i}/></div>;
 })}
 {active&&<div style={{position:'absolute',left:55,right:55,bottom:30,minHeight:75,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',fontSize:28,fontWeight:600,lineHeight:1.5,whiteSpace:'pre-line',color:active.who==='takosan'?'#39444b':'#725198',WebkitTextStroke:'2px #fff',paintOrder:'stroke fill'}}>{active.caption}</div>}
 {credits&&<div style={{position:'absolute',left:270,right:270,bottom:22,textAlign:'center',fontSize:14,lineHeight:1.6,color:'#777269',opacity:interpolate(f,[m.composition.durationInFrames-140,m.composition.durationInFrames-125],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}>音声：VOICEVOX:Voidoll ／ Irodori-TTS<br/>BGM：昼下がり気分／KK・ほのぼのワルツ【リコーダー】／エクシエ<br/>Music: TheFatRat - Unity</div>}
 </>}
 </AbsoluteFill>;
};
export const Root:React.FC=()=> <Composition id="KikouFive" component={Film} {...m.composition}/>;
