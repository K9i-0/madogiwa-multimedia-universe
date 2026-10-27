import {Html5Audio, Sequence, staticFile} from 'remotion';
import {Solo} from './Solo';
import m from './solo-sfx-manifest.json';
export const SoloSfx: React.FC = () => <>
 <Solo />
 {m.events.map((cue,i)=><Sequence key={i} from={cue.startFrame} durationInFrames={cue.durationInFrames}><Html5Audio src={staticFile(cue.file)} volume={cue.volume}/></Sequence>)}
</>;
