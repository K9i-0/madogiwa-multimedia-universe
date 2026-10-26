import {registerRoot,Composition} from 'remotion';
import {H3Film} from './H3Film';
import manifest from './edit-manifest-h3.json';
registerRoot(()=> <Composition id='MadogiwaKeynoteH3' component={H3Film} width={manifest.width} height={manifest.height} fps={manifest.fps} durationInFrames={manifest.durationInFrames}/>);
