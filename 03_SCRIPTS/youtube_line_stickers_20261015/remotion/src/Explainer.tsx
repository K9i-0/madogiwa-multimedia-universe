import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate} from 'remotion';
import rawManifest from './edit-manifest.json';
import {DuoSprite} from './DuoSprite';
import {captionColors,theme} from './theme';
import {SpreadsheetFrame} from './SpreadsheetFrame';
import {VisualAid} from './VisualAid';
import type {Manifest,Who,Mood} from './types';

const moodFor=(who:Who,d:Manifest['dialogue'][number]|undefined):Mood=>{
 const alias:Record<string,Mood>={worried:'worry',surprised:'surprise'};
 const given=d?.moods?.[who];if(given)return alias[given]??given;
 const id=d?.id??'';
 const specific:Record<string,[Mood,Mood]>={
  'intro-01':['worry','normal'],'intro-02':['worry','happy'],'intro-03':['bored','normal'],
  'intro-04':['normal','normal'],'intro-05':['happy','normal'],'intro-06':['normal','normal'],
  'intro-07':['worry','normal'],'intro-08':['surprise','normal'],'intro-09':['surprise','normal'],
  'intro-10':['angry','normal'],'intro-11':['angry','normal'],'intro-12':['angry','happy'],'intro-13':['surprise','normal'],
  'main-01':['happy','normal'],'main-02':['happy','happy'], 'main-05':['happy','normal'],
  'still-02':['smug','normal'],'still-04':['happy','normal'],'still-09':['worry','normal'],
  'sheet-01':['surprise','normal'],'sheet-03':['happy','normal'],'sheet-06':['worry','normal'],'sheet-09':['worry','normal'],
  'motion-01':['happy','normal'],'motion-03':['bored','normal'],'motion-05':['normal','happy'],
  'alpha-01':['happy','normal'],'alpha-02':['happy','normal'],'alpha-03':['bored','normal'],'alpha-05':['smug','normal'],
  'alpha-06':['surprise','normal'],'alpha-07':['sad','normal'],'alpha-11':['bored','normal'],
  'export-03':['surprise','normal'],'export-06':['worry','normal'],'record-05':['normal','happy'],
  'end-01':['smug','normal'],'end-02':['smug','normal'],'end-03':['smug','normal'],'end-04':['smug','happy'],'end-05':['bored','normal'],
 };
 return specific[id]?.[who==='yametaro'?0:1]??'normal';
};

export const Explainer:React.FC<{manifest?:Manifest;audioSrc?:string;hideCaptions?:boolean;silentPreview?:boolean}>=({manifest,audioSrc,hideCaptions=false,silentPreview=false})=>{
 const m=manifest??rawManifest as Manifest;const f=useCurrentFrame();
 const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);
 const previous=m.dialogue.reduce((last,d)=>f>=d.startFrame?d:last,m.dialogue[0]);
 const introLast=m.dialogue.find(d=>d.id==='intro-13');
 const titleStart=introLast?introLast.startFrame+introLast.durationInFrames+24:-999;
 const titleScene=m.scenes?.find(s=>f>=s.startFrame&&f<s.startFrame+s.durationInFrames);
 const title=titleScene?.view==='title'||(f>=titleStart&&f<titleStart+60);
 const caption=active?.captionSegments?.find(s=>f-active.startFrame>=s.startFrame&&f-active.startFrame<s.endFrame)?.text??active?.caption??active?.text;
 const mailTurn=m.dialogue.find(d=>d.id==='intro-07');
 const chatStart=m.dialogue.find(d=>d.id==='intro-04')?.startFrame??0;
 const greeting=m.dialogue.find(d=>d.id==='main-01');
 const afterTitle=Boolean(greeting&&f>=titleStart+60&&f<greeting.startFrame&&f>titleStart);
 const previewChat=chatStart>0&&f>=chatStart-12&&f<chatStart;
 const openMail=mailTurn&&f>=mailTurn.startFrame+mailTurn.durationInFrames+9&&previous?.id==='intro-07';
 const view=title?'title':titleScene?.view??(afterTitle?'greeting':previewChat?'line-chat':openMail?'outlook':previous?.view??'opening-grid');
 return <AbsoluteFill style={{background:'#fff',fontFamily:'"Hiragino Sans",sans-serif',color:theme.ink}}>
  {!silentPreview&&<Audio src={staticFile(audioSrc??m.audioSrc??'mixed.wav')}/>}
  {title?<AbsoluteFill style={{background:theme.blue,color:'white',justifyContent:'center',alignItems:'center'}}>
   <div style={{fontSize:26,letterSpacing:5,marginBottom:28,opacity:.85}}>窓際族物語・制作ノート</div>
   <div style={{fontSize:57,fontWeight:800,lineHeight:1.45,textAlign:'center'}}>Codexで<br/>動くLINEスタンプを作る</div>
   <div style={{fontSize:21,marginTop:40}}>やめ太郎 ＆ たこさん</div>
  </AbsoluteFill>:<SpreadsheetFrame chapter={previous?.chapter}>
    <div style={{position:'absolute',left:260,top:106,width:760,height:485,transform:'scale(.90)',transformOrigin:'top center',background:'#fff',display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',textAlign:'center'}}>
     <VisualAid view={view} frame={f} utterance={previous} chatStart={chatStart}/>
    </div>
    {(['yametaro','takosan'] as Who[]).map(who=>{
     const speaking=active?.who===who;const local=active?f-active.startFrame:0;
     const peak=Math.max(...(active?.envelope??[0]));
     const level=active?.envelope?.[Math.floor(local/2)*2]??0;
     const open=speaking&&level>Math.max(.0025,peak*.15);
     const mood=moodFor(who,afterTitle?greeting:previous);
     return <DuoSprite key={who} who={who} speaking={speaking} open={open} mood={mood} local={local}/>;
    })}
    {active&&!hideCaptions&&<div style={{position:'absolute',left:245,right:245,bottom:42,minHeight:112,boxSizing:'border-box',padding:'8px 5px',background:'#fff',borderTop:'1px solid #cbd4ce',display:'flex',alignItems:'center',justifyContent:'center'}}>
      <div style={{fontSize:active.captionFontSize??29,fontWeight:700,lineHeight:1.55,textAlign:'center',whiteSpace:'pre-line',color:captionColors[active.who],WebkitTextStroke:'3px #fff',paintOrder:'stroke fill'}}>{caption}</div>
    </div>}
  </SpreadsheetFrame>}
  <AbsoluteFill style={{pointerEvents:'none',background:'#fff',opacity:interpolate(f,[m.composition.durationInFrames-45,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
 </AbsoluteFill>;
};
