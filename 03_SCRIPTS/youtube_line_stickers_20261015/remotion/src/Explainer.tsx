import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate} from 'remotion';
import shorts from '../../shorts-manifest.json';
import {memberCaptionStyle} from '../../../00_TEMPLATES/subtitles/member-colors';
import rawManifest from './edit-manifest.json';
import {DuoSprite} from './DuoSprite';
import {captionColors,theme} from './theme';
import {SpreadsheetFrame} from './SpreadsheetFrame';
import {VisualAid} from './VisualAid';
import {TipsVisualAid,tipsViews} from './TipsVisualAid';
import type {Manifest,Who,Mood} from './types';

const moodFor=(who:Who,d:Manifest['dialogue'][number]|undefined):Mood=>{
 const alias:Record<string,Mood>={worried:'worry',surprised:'surprise'};
 const given=d?.moods?.[who];if(given)return alias[given]??given;
 const id=d?.id??'';
 const specific:Record<string,[Mood,Mood]>={
  'intro-01':['worry','normal'],'intro-02':['worry','happy'],'intro-03':['bored','normal'],
  'intro-04':['normal','normal'],'intro-05':['normal','normal'],'intro-06':['normal','normal'],
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
  'tips-02':['happy','normal'],'tips-04':['surprise','normal'],'tips-second-02':['surprise','normal'],
  'ideas-01':['smug','normal'],'ideas-03':['surprise','normal'],'ideas-06':['bored','normal'],'ideas-08':['worry','normal'],
  'options-01':['worry','normal'],'options-03':['surprise','normal'],'options-05':['bored','normal'],'options-06b':['angry','normal'],'options-07':['happy','normal'],'options-09':['smug','normal'],
  'redraw-01':['worry','normal'],'redraw-03':['worry','normal'],'redraw-06':['happy','normal'],
  'pets-01':['surprise','normal'],'pets-05':['bored','happy'],'pets-07':['happy','normal'],
  'acting-01':['worry','normal'],'acting-03':['happy','normal'],'acting-06':['bored','normal'],'acting-06b':['bored','normal'],'acting-06c':['bored','normal'],'acting-08':['surprise','normal'],'acting-10':['happy','normal'],'acting-12':['worry','normal'],
  'inspect-03':['surprise','normal'],'inspect-04b':['bored','normal'],'inspect-06':['worry','normal'],
  'tools-01':['normal','normal'],'tools-03':['surprise','normal'],'tools-05':['surprise','normal'],'tools-07b':['bored','normal'],'tools-08':['happy','normal'],
  'close-01':['happy','normal'],'close-02':['happy','happy'],'close-04':['smug','normal'],'close-05':['bored','normal'],
 };
 return specific[id]?.[who==='yametaro'?0:1]??'normal';
};

export const Explainer:React.FC<{manifest?:Manifest;audioSrc?:string;hideCaptions?:boolean;silentPreview?:boolean;portrait?:boolean}>=({manifest,audioSrc,hideCaptions=false,silentPreview=false,portrait=false})=>{
 const m=manifest??rawManifest as Manifest;const f=useCurrentFrame();
 const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);
 const previous=m.dialogue.reduce((last,d)=>f>=d.startFrame?d:last,m.dialogue[0]);
 const introLast=[...m.dialogue].reverse().find(d=>d.id.startsWith('intro-'));
 // Whole-screen white dip: 6-frame hold, 12-frame out, 12-frame in.
 // The greeting replaces the cold-open exactly at the all-white midpoint.
 const introEnd=introLast?introLast.startFrame+introLast.durationInFrames:undefined;
 const transitionMid=introEnd===undefined?undefined:introEnd+18;
 const transitionOpacity=introEnd===undefined?0:interpolate(f,[introEnd+6,introEnd+18,introEnd+30],[0,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 const scene=m.scenes?.find(s=>s.view!=='title'&&f>=s.startFrame&&f<s.startFrame+s.durationInFrames);
 const caption=active?.captionSegments?.find(s=>f-active.startFrame>=s.startFrame&&f-active.startFrame<s.endFrame)?.text??active?.caption??active?.text;
 const mailTurn=m.dialogue.find(d=>d.id==='intro-07');
 const chatStart=m.dialogue.find(d=>d.id==='intro-04')?.startFrame??0;
 const greeting=m.dialogue.find(d=>d.id==='main-01');
 const greetingPreview=Boolean(greeting&&transitionMid!==undefined&&f>=transitionMid&&f<greeting.startFrame);
 const visualTurn=greetingPreview?greeting:previous;
 const previewChat=chatStart>0&&f>=chatStart-12&&f<chatStart;
 const openMail=mailTurn&&f>=mailTurn.startFrame+mailTurn.durationInFrames+9&&previous?.id==='intro-07';
 const view=greetingPreview?'greeting':scene?.view??(previewChat?'line-chat':openMail?'outlook':previous?.view??'opening-grid');
 const tips=Boolean(previous&&tipsViews.has(view)&&!previous.id.startsWith('intro-')&&!['main-01','main-02','main-03'].includes(previous.id));
 const previousIndex=m.dialogue.indexOf(previous);let viewIndex=previousIndex;
 while(viewIndex>0&&m.dialogue[viewIndex-1].view===view)viewIndex--;
 const viewStart=m.dialogue[viewIndex]?.startFrame;
 if(portrait){
  const c=shorts.captions.find(c=>f>=c.startFrame&&f<c.endFrame);
  const lines=shorts.titleCues.reduce((lines,cue)=>f>=cue.from?cue.titleLines:lines,shorts.titleLines);
  return <AbsoluteFill style={{background:'#102c24',fontFamily:'"Hiragino Sans",sans-serif',color:'#fff',overflow:'hidden'}}>
   <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 50%,#2c5948,#102c24 80%)'}}/>
   <div style={{position:'absolute',top:76,left:24,right:24,textAlign:'center',fontWeight:700}}><div style={{fontSize:29,marginBottom:14}}>{lines[0]}</div><div style={{fontSize:56,color:'#fff2d4'}}>{lines[1]}</div></div>
   <div style={{position:'absolute',left:0,top:240,width:720,height:455,background:'#fff',overflow:'hidden'}}>
    <div style={{position:'absolute',left:18,top:9,width:760,height:485,transform:'scale(.9)',transformOrigin:'top left',display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',textAlign:'center',color:theme.ink}}>
     {tips?<TipsVisualAid view={view} frame={f} utterance={previous} viewStart={viewStart}/>:<VisualAid view={view} frame={f} utterance={visualTurn} chatStart={chatStart}/>}
    </div>
   </div>
   {(['yametaro','takosan'] as Who[]).map(who=>{
    const local=active?f-active.startFrame:0;const speaking=active?.who===who;
    const peak=Math.max(...(active?.envelope??[0]));const level=active?.envelope?.[Math.floor(local/2)*2]??0;
    return <DuoSprite key={who} who={who} speaking={speaking} open={speaking&&level>Math.max(.0025,peak*.15)} mood={moodFor(who,visualTurn)} local={local} portrait/>;
   })}
   {c&&<div style={{position:'absolute',top:1030,left:30,right:30,textAlign:'center',fontWeight:700}}><div style={{fontSize:26,marginBottom:10}}>{c.speaker}</div><div style={{fontSize:36,lineHeight:1.45,whiteSpace:'pre-line',...memberCaptionStyle(c.speaker)}}>{c.text}</div></div>}
   <AbsoluteFill style={{pointerEvents:'none',background:'#fff',opacity:transitionOpacity}}/>
  </AbsoluteFill>;
 }
 return <AbsoluteFill style={{background:'#fff',fontFamily:'"Hiragino Sans",sans-serif',color:theme.ink}}>
  {!silentPreview&&<Audio src={staticFile(audioSrc??m.audioSrc??'mixed.wav')}/>}
  <SpreadsheetFrame chapter={visualTurn?.chapter} variant={tips?'tips':'original'}>
    <div style={{position:'absolute',left:260,top:106,width:760,height:485,transform:'scale(.90)',transformOrigin:'top center',background:'#fff',display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',textAlign:'center'}}>
     {tips?<TipsVisualAid view={view} frame={f} utterance={previous} viewStart={viewStart}/>:<VisualAid view={view} frame={f} utterance={visualTurn} chatStart={chatStart}/>}
    </div>
    {(['yametaro','takosan'] as Who[]).map(who=>{
     const speaking=active?.who===who;const local=active?f-active.startFrame:0;
     const peak=Math.max(...(active?.envelope??[0]));
     const level=active?.envelope?.[Math.floor(local/2)*2]??0;
     const open=speaking&&level>Math.max(.0025,peak*.15);
     const mood=moodFor(who,visualTurn);
     return <DuoSprite key={who} who={who} speaking={speaking} open={open} mood={mood} local={local}/>;
    })}
    {active&&!hideCaptions&&<div style={{position:'absolute',left:245,right:245,bottom:42,minHeight:112,boxSizing:'border-box',padding:'8px 5px',background:'#fff',borderTop:'1px solid #cbd4ce',display:'flex',alignItems:'center',justifyContent:'center'}}>
      <div style={{fontSize:active.captionFontSize??29,fontWeight:700,lineHeight:1.55,textAlign:'center',whiteSpace:'pre-line',color:captionColors[active.who],WebkitTextStroke:'3px #fff',paintOrder:'stroke fill'}}>{caption}</div>
    </div>}
  </SpreadsheetFrame>
  <AbsoluteFill style={{pointerEvents:'none',background:'#fff',opacity:transitionOpacity}}/>
  <AbsoluteFill style={{pointerEvents:'none',background:'#fff',opacity:interpolate(f,[m.composition.durationInFrames-45,m.composition.durationInFrames-1],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}/>
 </AbsoluteFill>;
};
