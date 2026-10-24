import React from 'react';
import {AbsoluteFill, Audio, Freeze, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame, interpolate} from 'remotion';
import manifest from './edit-manifest.json';
import {ComparisonGraphic} from './NewsGraphics';
import {memberColor} from '../../../00_TEMPLATES/subtitles/member-colors';

export const finalSpec = manifest.final;
const ink = '#183a62';
const gain = (key:keyof typeof finalSpec.audioGainDb) => Math.pow(10,finalSpec.audioGainDb[key]/20);
const clipVolume = (id:string, f:number) => id==='theft' ? interpolate(f,[100,108],[gain('theft'),gain('theftAction')],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}) : id==='harvest_broll' ? 0 : gain(id as keyof typeof finalSpec.audioGainDb);
const font = '"Hiragino Sans", "Hiragino Kaku Gothic ProN", sans-serif';
const full: React.CSSProperties = {width:'100%', height:'100%', objectFit:'cover'};
const fade = (f:number) => interpolate(f,[0,5],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});

// Deterministic handheld pursuit: move only the camera image, never broadcast graphics.
const chaseStyle = (f:number):React.CSSProperties => {
  const c=finalSpec.chaseCamera;
  const a=interpolate(f,c.frames,c.strength,{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
  const t=f-c.frames[0];
  const x=a*c.translationX*(0.65*Math.sin(t*0.83)+0.35*Math.sin(t*1.71+0.4));
  const y=a*c.translationY*(0.7*Math.sin(t*1.11+0.8)+0.3*Math.sin(t*2.03));
  const r=a*c.rotationDegrees*(0.7*Math.sin(t*0.51)+0.3*Math.sin(t*1.43));
  return {...full,transform:`translate(${x}px,${y}px) rotate(${r}deg) scale(${1+a*c.overscan})`};
};

const Header = ({live=false, studio=false, document=false}:{live?:boolean;studio?:boolean;document?:boolean}) => <>
  {!document&&<div style={{position:'absolute',inset:0,background:'linear-gradient(#0005,transparent 23%,transparent 78%,#0003)',pointerEvents:'none'}}/>}
  <div style={{position:'absolute',left:50,top:25,color:document?ink:'white',fontSize:38,fontWeight:700,fontFamily:'Arial',textShadow:document?'none':'0 1px 4px #0009'}}>{finalSpec.clock}</div>
  <div style={{position:'absolute',right:0,top:0,width:278,height:92,background:studio?ink:'transparent',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',color:document?ink:'white',textShadow:studio||document?'none':'0 1px 4px #0009'}}>
    <div style={{fontSize:30,fontWeight:600,letterSpacing:2}}>ゆめテレ <span style={{fontSize:15,letterSpacing:1}}>NEWS</span></div>
    <div style={{fontSize:17,marginTop:4,letterSpacing:1}}>秋の味覚　ちくわ狩り</div>
  </div>
  {live && <div style={{position:'absolute',top:84,left:50,color:'white',fontSize:18,letterSpacing:2,display:'flex'}}><span style={{background:'#a43443',padding:'4px 10px'}}>中継</span><span style={{background:'#132838d9',padding:'4px 12px'}}>ちくわ狩りの現場</span></div>}
</>;

const Headline = ({returning=false,title}:{returning?:boolean;title?:string}) => <div style={{position:'absolute',left:0,right:0,bottom:0,height:142,background:'#f8fafc',borderTop:`4px solid ${ink}`,padding:'17px 50px',color:ink}}>
  <div style={{fontSize:18,letterSpacing:2,color:'#80683c',marginBottom:8}}>{returning?'ゆめテレ NEWS':'季節の話題'}</div>
  <div style={{fontSize:38,fontWeight:600,letterSpacing:1}}>{title??(returning?'中継をいったん失礼します':'秋の味覚　ちくわ狩り最盛期')}</div>
</div>;

const ExpertName = () => <div style={{position:'absolute',left:50,bottom:40,padding:'13px 22px',color:ink,background:'rgba(250,252,254,.95)',borderLeft:`5px solid ${memberColor('おかやまん')}`}}>
  <div style={{fontSize:20}}>窓際大学大学院 農学研究科　准教授</div>
  <div style={{fontSize:35,fontWeight:600,marginTop:5}}>おかやまん<span style={{fontSize:19,fontWeight:500,marginLeft:24}}>専門：ちくわ生物学</span></div>
</div>;

const Bridge = ({expert}:{expert:boolean}) => {
  const f=useCurrentFrame();
  const cue=finalSpec.smoothCuts.introAudioFrom;
  if (!expert) return <AbsoluteFill>
    <Sequence durationInFrames={finalSpec.smoothCuts.fieldFrom}><ComparisonGraphic showHeader={false} message="reaction" anchorReply/><Header document/></Sequence>
    <Sequence from={finalSpec.smoothCuts.fieldFrom}><Img src={staticFile('forest_v2.png')} style={full}/><Header/><div style={{position:'absolute',left:50,bottom:45,color:'white',fontSize:36,fontWeight:600,textShadow:'0 2px 5px #000'}}>秋のちくわ狩り</div></Sequence>
    <Audio src={staticFile('voice_anchor_comparison_reply.wav')}/>
  </AbsoluteFill>;
  const listeningFrom=finalSpec.coherentExpert.listeningFrom;
  return <AbsoluteFill>
    <Sequence durationInFrames={listeningFrom}><Img src={staticFile('forest_v2.png')} style={full}/><Header/><Headline title="天然のちくわ　採取には注意が必要"/></Sequence>
    <Sequence from={listeningFrom}><Freeze frame={Math.min(Math.max(0,f-listeningFrom),179)}><OffthreadVideo src={staticFile('expert_listening.mp4')} muted style={full}/></Freeze><Header/><ExpertName/></Sequence>
    <Sequence from={cue}><Audio src={staticFile('voice_anchor_expert_intro.wav')}/></Sequence>
  </AbsoluteFill>;
};

const Caption = ({speaker,text}:{speaker:string;text:string}) => {
  const f=useCurrentFrame();
  return <div style={{position:'absolute',left:50,bottom:40,maxWidth:1180,opacity:fade(f),color:ink,background:'rgba(250,252,254,.94)',borderLeft:`5px solid ${memberColor(speaker)}`,padding:'10px 20px 13px',boxShadow:'0 2px 8px #0002'}}>
    <div style={{fontSize:18,fontWeight:500,marginBottom:5}}>{speaker}<span style={{marginLeft:14,color:'#566675',fontSize:16}}>ちくわ狩りに訪れた人</span></div>
    <div style={{fontSize:36,fontWeight:600,lineHeight:1.25,letterSpacing:.3}}>{text}</div>
  </div>;
};

const Shot = ({id,showCaptions=true}:{id:string;showCaptions?:boolean}) => {
  const f=useCurrentFrame();
  const video = ['harvest_broll','yotan','fukugyun','expert','theft'].includes(id);
  return <AbsoluteFill style={{overflow:'hidden'}}>
    {id==='intro' && <><OffthreadVideo src={staticFile('anchor_intro.mp4')} volume={gain('intro')} style={full}/><Header studio/><Headline/></>}
    {id==='forest' && <><Img src={staticFile('forest_v2.png')} style={full}/><Header/><div style={{position:'absolute',bottom:46,left:50,color:'white',textShadow:'0 2px 5px #000',opacity:fade(f)}}><div style={{fontSize:19,marginBottom:9,letterSpacing:2}}>秋の味覚</div><div style={{fontSize:39,fontWeight:600}}>天然ちくわ　収穫の季節</div></div></>}
    {video && <><OffthreadVideo src={staticFile(`edit_${id}.mp4`)} volume={(frame)=>clipVolume(id,frame)} style={id==='theft'?chaseStyle(f):full}/><Header live={id!=='expert'}/></>}
    {id==='expert' && <ExpertName/>}
    {id==='bridge_expert' && <Bridge expert/>}
    {id==='bridge_field' && <Bridge expert={false}/>}
    {id==='comparison' && <><ComparisonGraphic expertPortrait expertMotion showHeader={false} message={f>=finalSpec.beerExplanation.beerClueFrom?'beer':'appearance'}/><Header document/><Audio src={staticFile('voice_expert_beer_continuation.wav')}/></>}
    {id==='theft' && <Sequence from={finalSpec.feedback.sobayaFrom} durationInFrames={finalSpec.feedback.sobayaFrames}><Audio src={staticFile('voice_sobaya_poison.wav')}/></Sequence>}
    {id==='standby' && <><Img src={staticFile('forest_v2.png')} style={full}/><AbsoluteFill style={{background:'#10243755'}}/><Header/><div style={{position:'absolute',left:0,right:0,top:284,padding:'25px 0',background:'rgba(248,250,252,.94)',color:ink,textAlign:'center',borderTop:'1px solid #e0e6eb',borderBottom:'1px solid #e0e6eb'}}><div style={{fontSize:37,fontWeight:600,letterSpacing:2}}>中継を中断しています</div><div style={{fontSize:22,marginTop:12,letterSpacing:2}}>しばらくお待ちください</div></div><Sequence from={finalSpec.smoothCuts.interruptionAudioFrom}><Audio src={staticFile('voice_interruption.wav')} volume={gain('interruption')}/></Sequence></>}
    {showCaptions&&finalSpec.captions.filter(c=>c.shot===id).map((c,i)=><Sequence key={i} from={c.from} durationInFrames={c.to-c.from}><Caption speaker={c.speaker} text={c.text}/></Sequence>)}
  </AbsoluteFill>;
};

export const FinalNews = ({showCaptions=true}:{showCaptions?:boolean}) => <AbsoluteFill style={{background:'#182d43',fontFamily:font,fontSynthesis:'none',WebkitFontSmoothing:'antialiased'}}>
  {finalSpec.sequences.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.duration}><Shot id={s.id} showCaptions={showCaptions}/></Sequence>)}
  <Sequence from={finalSpec.sequences.find(s=>s.id==='forest')!.from} durationInFrames={132}><Audio src={staticFile('voice_forest.wav')} volume={gain('forest')}/></Sequence>
  <Sequence from={finalSpec.sequences.find(s=>s.id==='harvest_broll')!.from} durationInFrames={66}><Audio src={staticFile('field_ambience.wav')} volume={0.5}/></Sequence>
</AbsoluteFill>;
