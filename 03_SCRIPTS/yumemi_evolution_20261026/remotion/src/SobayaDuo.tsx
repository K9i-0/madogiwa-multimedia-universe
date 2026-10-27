import {Video} from '@remotion/media';
import {AbsoluteFill, Html5Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import m from './sobaya-manifest.json';
export const SobayaDuo: React.FC = () => {
 const frame=useCurrentFrame();
 const a=m.lines.find(l=>l.speaker==='anchor' && frame>=l.startFrame && frame<l.endFrame);
 const b=m.lines.find(l=>l.speaker==='sobaya' && frame>=l.startFrame && frame<l.endFrame);
 const mouth=!!b&&(b.envelope[Math.min(frame-b.startFrame,b.envelope.length-1)]??0)>.12&&frame%7<5;
 return <AbsoluteFill style={{background:'#160f25'}}>
  <div style={{position:'absolute',inset:0,overflow:'hidden'}}>
   {m.scenes.map(s=><Sequence key={s.startFrame} from={s.startFrame} durationInFrames={s.durationInFrames} layout="none">
    <Video src={staticFile('input.mp4')} trimBefore={s.sourceStartFrame} trimAfter={s.sourceEndFrame} playbackRate={s.playbackRate} muted style={{width:'100%',height:'100%'}} />
   </Sequence>)}
  </div>
  <Img src={staticFile('duo/yumemin.png')} style={{position:'absolute',left:-30,bottom:125,width:310,transform:`scaleX(-1) translateY(${a?-Math.abs(Math.sin(frame*.34))*7:0}px)`,filter:a?'drop-shadow(0 0 12px #38badd66)':'none'}}/>
  <div style={{position:'absolute',right:-70,bottom:140,width:460,height:460*1351/1164,transform:`translateY(${b?-Math.abs(Math.sin((frame-b.startFrame)*.5))*5:0}px)`}}>
   <Img src={staticFile('sobaya/sobaya_normal.png')} style={{position:'absolute',width:'100%',height:'100%'}}/>
   {mouth&&<Img src={staticFile('sobaya/sobaya_normal_talk.png')} style={{position:'absolute',width:'100%',height:'100%',clipPath:`inset(${300/1351*100}% ${(1164-477-64)/1164*100}% ${(1351-300-63)/1351*100}% ${477/1164*100}%)`}}/>}
  </div>
  {m.lines.map(l=><Sequence key={l.id} from={l.startFrame} durationInFrames={l.durationInFrames}><Html5Audio src={staticFile(l.file)} trimBefore={l.trimBefore} volume={l.volume}/></Sequence>)}
 </AbsoluteFill>;
};
