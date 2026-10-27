import {AbsoluteFill,Html5Audio,Sequence,staticFile} from 'remotion';
import {Relaxed} from './Relaxed';
import sfx from './familiar-sfx-manifest.json';
export const Familiar: React.FC=()=> <AbsoluteFill><Relaxed/>{sfx.events.map((e,i)=><Sequence key={i} from={e.startFrame} durationInFrames={e.durationInFrames}><Html5Audio src={staticFile(e.file)} volume={f=>e.volume*Math.min(1,(e.durationInFrames-f)/4)}/></Sequence>)}</AbsoluteFill>;
