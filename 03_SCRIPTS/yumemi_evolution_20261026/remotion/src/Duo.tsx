import {Video} from '@remotion/media';
import {AbsoluteFill, Html5Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import m from './duo-manifest.json';
import {memberCaptionStyle} from './member-colors';
export const Duo: React.FC = () => {
 const frame=useCurrentFrame();
 const speaking=(speaker:string)=>m.lines.find(l=>l.speaker===speaker && frame>=l.startFrame && frame<l.endFrame);
 const a=speaking('anchor'), y=speaking('yametaro');
 const lastY=[...m.lines].reverse().find(l=>l.speaker==='yametaro'&&frame>=l.startFrame);
 const mood=y?.mood??lastY?.mood??'normal';
 const mouth=!!y && (y.envelope[Math.min(frame-y.startFrame,y.envelope.length-1)]??0)>0.12 && frame%7<5;
 const caption=y??a;
 return <AbsoluteFill style={{background:'#160f25'}}>
  <div style={{position:'absolute',inset:0,overflow:'hidden'}}>
   {m.scenes.map(s=><Sequence key={s.startFrame} from={s.startFrame} durationInFrames={s.durationInFrames} layout="none">
    <Video src={staticFile('input.mp4')} trimBefore={s.sourceStartFrame} trimAfter={s.sourceEndFrame} playbackRate={s.playbackRate} muted style={{width:'100%',height:'100%'}} />
   </Sequence>)}
  </div>
  <Img src={staticFile('duo/yumemin.png')} style={{position:'absolute',left:-30,bottom:125,width:310,transform:`scaleX(-1) translateY(${a?-Math.abs(Math.sin(frame*.34))*7:0}px)`,filter:a?'drop-shadow(0 0 12px #38badd66)':'none'}}/>
  <Img src={staticFile(`duo/yametaro_${mood}_${mouth?'open':'closed'}.png`)} style={{position:'absolute',right:-35,bottom:100,width:270,transform:`translateY(${y?-Math.abs(Math.sin((frame-y.startFrame)*.5))*6:0}px)`,filter:y?'drop-shadow(0 0 10px #b389ec77)':'none'}}/>
  {caption&&<div style={{position:'absolute',left:220,right:650,top:28,textAlign:'center',fontFamily:'"Hiragino Sans",sans-serif',fontWeight:800,fontSize:40,lineHeight:1.42,whiteSpace:'pre-line',...memberCaptionStyle(caption.speaker==='anchor'?'ゆめみん':'やめ太郎')}}>{caption.caption}</div>}
  {m.lines.map(l=><Sequence key={l.id} from={l.startFrame} durationInFrames={l.durationInFrames}><Html5Audio src={staticFile(l.file)} trimBefore={l.trimBefore} volume={l.volume}/></Sequence>)}
 </AbsoluteFill>;
};
