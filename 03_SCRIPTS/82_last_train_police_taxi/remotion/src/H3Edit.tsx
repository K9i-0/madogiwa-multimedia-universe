import React from 'react';
import {AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, staticFile} from 'remotion';
import data from './h3-edit.json';
export const H3Edit: React.FC = () => <AbsoluteFill style={{backgroundColor:'black'}}>
 {data.shots.map((s,index)=><Sequence key={index} from={s.from} durationInFrames={s.duration}>
  <OffthreadVideo src={staticFile(s.file)} muted startFrom={s.sourceStart} endAt={s.sourceEnd}
   playbackRate={(s.sourceEnd-s.sourceStart)/s.duration}
   style={{width:'100%',height:'100%',objectFit:'contain'}} />
 </Sequence>)}
 {data.dialogue.map(d=><Sequence key={d.id} from={d.from} durationInFrames={d.duration}>
  <Audio src={staticFile(d.file)} volume={d.volume}/>
 </Sequence>)}
 {data.effects.map((e,index)=><Sequence key={index} from={e.from} durationInFrames={e.duration}>
  <Audio src={staticFile(e.file)} volume={frame=>interpolate(frame,[0,Math.min(3,e.duration/4),Math.max(4,e.duration-6),e.duration],[0,e.volume,e.volume,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/>
 </Sequence>)}
 <Sequence from={data.siren.from} durationInFrames={data.composition.durationInFrames-data.siren.from}>
  <Audio src={staticFile('police_siren_wan71.wav')} loop loopVolumeCurveBehavior="extend"
   volume={frame=>interpolate(frame,data.siren.volumeFrames,data.siren.volumes,{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}/>
 </Sequence>
</AbsoluteFill>;
