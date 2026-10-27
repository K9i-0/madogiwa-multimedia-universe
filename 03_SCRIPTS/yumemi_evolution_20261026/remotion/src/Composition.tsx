import {Video} from '@remotion/media';
import {AbsoluteFill, Html5Audio, Sequence, staticFile} from 'remotion';
import manifest from './edit-manifest.json';
export const EditComposition: React.FC<{manifest: unknown}> = () => <AbsoluteFill style={{backgroundColor: '#000'}}>
  <Video src={staticFile(manifest.inputVideo)} muted style={{width:'100%',height:'100%'}} />
  {manifest.audioClips.map((clip) => <Sequence key={clip.startFrame} from={clip.startFrame} durationInFrames={clip.durationInFrames}>
    <Html5Audio src={staticFile(clip.file)} trimBefore={clip.sourceStartFrame} volume={0.85} />
  </Sequence>)}
</AbsoluteFill>;
