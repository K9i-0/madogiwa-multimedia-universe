import React from 'react';
import {AbsoluteFill,Audio,Img,OffthreadVideo,Sequence,staticFile,useCurrentFrame} from 'remotion';
import m from './edit-manifest.json';
const Picture:React.FC<{name:string;wide?:boolean}>=({name,wide=false})=><Img src={staticFile(name)} style={{width:wide?680:470,height:wide?383:470,objectFit:'contain'}}/>;
const Center:React.FC<{view:string}>=({view})=>{
 const title=(t:string)=><div style={{fontSize:38,fontWeight:700,lineHeight:1.7,whiteSpace:'pre-line'}}>{t}</div>;
 if(view==='intro')return <>{title('アーロンチュアとは何か')}<div style={{fontSize:26,marginTop:26,color:'#687367'}}>高級そうな、段ボール椅子の歴史</div><Img src={staticFile('episode_01.png')} style={{width:260,height:260,marginTop:24}}/></>;
 if(view==='origin')return <>{title('アーロンチェア')}<div style={{fontSize:23,margin:'12px 0 25px'}}>Herman Miller</div><div style={{fontSize:30,color:'#8d397c'}}>↓</div>{title('アーロンチュア')}<div style={{fontSize:24,marginTop:15}}>「チュア」はアクシデンチュアから</div></>;
 if(view==='manga1'||view==='manga2')return <Picture name={view==='manga1'?'episode_01.png':'episode_02.png'}/>;
 if(['yotan','cto','window'].includes(view))return <><Picture name="workshop.png" wide/>{title('よーたん')}{view!=='yotan'&&<div style={{fontSize:29,marginTop:8}}>アクシデンチュアのCTO</div>}{view==='window'&&<div style={{fontSize:31,marginTop:8,color:'#8d397c'}}>でも、窓際族。</div>}</>;
 if(view==='summary')return <>{title('愛用品から、家庭用キットへ')}<div style={{display:'flex',gap:18,alignItems:'center',marginTop:35}}>{['episode_01.png','workshop.png','kit.png'].map((name,i)=><React.Fragment key={name}>{i>0&&<span style={{fontSize:24}}>→</span>}<div><Img src={staticFile(name)} style={{width:180,height:170,objectFit:'contain'}}/><div style={{fontSize:23,marginTop:12}}>{['第一話','社員のDIY','創刊号399円'][i]}</div></div></React.Fragment>)}</div></>;
 return <Picture name={`${['workshop','seated','kit','kitroom'].includes(view)?view:'kit'}.png`} wide/>;
};
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);
 const previous=[...m.dialogue].reverse().find(d=>f>=d.startFrame);const clip=m.clips.find(c=>f>=c.startFrame&&f<c.startFrame+c.durationInFrames);const credits=f>=m.creditsStartFrame;
 return <AbsoluteFill style={{background:'#f3f0e6',fontFamily:'"Hiragino Sans", "Noto Sans JP", sans-serif',color:'#28353c'}}>
 <Audio src={staticFile('mixed.wav')}/>
 {!credits&&<>
 <div style={{position:'absolute',left:300,top:25,width:680,height:525,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',textAlign:'center'}}>
 {clip?<Sequence from={clip.startFrame} durationInFrames={clip.durationInFrames} layout="none"><OffthreadVideo muted src={staticFile(clip.src)} startFrom={clip.sourceStartFrame} style={{width:680,height:383,objectFit:'contain'}}/><div style={{fontSize:20,marginTop:14,color:'#687367'}}>{clip.label}</div></Sequence>:<Center view={previous?.view??'intro'}/>}
 </div>
 {(['zunda','metan'] as const).map((who,i)=>{const speaking=active?.who===who;const j=active?f-active.startFrame:0;const open=speaking&&(active?.envelope[j]??0)>.023;const blink=(f+(i?49:0))%127<4;const surprise=speaking&&who==='zunda'&&/偉い|どういう|暇なの/.test(active?.text??'');const mood=blink?'blink':surprise?'surprise':'normal';return <Img key={who} src={staticFile(`${who}_${mood}_${Number(open)}.png`)} style={{position:'absolute',left:i?990:0,bottom:0,width:290,transform:who==='zunda'?'scaleX(-1)':undefined}}/>;})}
 {active&&<div style={{position:'absolute',left:60,right:60,bottom:27,minHeight:106,display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{fontSize:30,fontWeight:700,lineHeight:1.6,textAlign:'center',whiteSpace:'pre-line',color:active.who==='zunda'?'#347526':'#8d397c',WebkitTextStroke:'6px #fff',paintOrder:'stroke fill',textShadow:'0 2px 3px #0003'}}>{active.caption}</div></div>}
 </>}
 {credits&&<AbsoluteFill style={{alignItems:'center',justifyContent:'center',fontSize:23,lineHeight:2,textAlign:'center'}}><div>音声：VOICEVOX:ずんだもん ／ VOICEVOX:四国めたん<br/>立ち絵：坂本アヒル 様<br/>導入BGM：昼下がり気分 ／ KK<br/>本編BGM：ほのぼのワルツ【リコーダー】／ エクシエ<br/>原作・資料映像：窓際族物語</div></AbsoluteFill>}
 </AbsoluteFill>;
};
