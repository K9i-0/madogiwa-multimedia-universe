import {Video} from '@remotion/media';
import {AbsoluteFill, Html5Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import m from './solo-manifest.json';
export const Solo: React.FC = () => {
 const frame=useCurrentFrame();
 const a=m.lines.find(l=>frame>=l.startFrame && frame<l.endFrame);
 return <AbsoluteFill style={{background:'#160f25'}}>
  <div style={{position:'absolute',inset:0,overflow:'hidden'}}>
   {m.scenes.map(s=><Sequence key={s.startFrame} from={s.startFrame} durationInFrames={s.durationInFrames} layout="none">
    <Video src={staticFile('input.mp4')} trimBefore={s.sourceStartFrame} trimAfter={s.sourceEndFrame} playbackRate={s.playbackRate} muted style={{width:'100%',height:'100%'}} />
   </Sequence>)}
  </div>
  <Img src={staticFile('duo/yumemin.png')} style={{position:'absolute',left:-30,bottom:125,width:310,transform:`scaleX(-1) translateY(${a?-Math.abs(Math.sin(frame*.34))*7:0}px)`,filter:a?'drop-shadow(0 0 12px #38badd66)':'none'}}/>
  {m.lines.map(l=><Sequence key={l.id} from={l.startFrame} durationInFrames={l.durationInFrames}><Html5Audio src={staticFile(l.file)} trimBefore={l.trimBefore} volume={l.volume}/></Sequence>)}
 </AbsoluteFill>;
};
