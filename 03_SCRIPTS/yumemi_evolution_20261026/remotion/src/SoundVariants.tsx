import {Html5Audio,Sequence,staticFile} from 'remotion';
import {Solo} from './Solo';
import keynote from './sound-keynote-manifest.json';
import comedy from './sound-comedy-manifest.json';
import intense from './sound-intense-manifest.json';
const choices={keynote,comedy,intense};
export const SoundVariants:React.FC<{variant:keyof typeof choices}>=({variant})=><>
 <Solo/>
 {choices[variant].events.map((e,i)=><Sequence key={i} from={e.startFrame} durationInFrames={e.durationInFrames}><Html5Audio src={staticFile(e.file)} volume={e.volume}/></Sequence>)}
</>;
