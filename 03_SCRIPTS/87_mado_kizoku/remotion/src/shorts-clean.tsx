import {Composition,registerRoot} from 'remotion';
import {FullFilm} from './ShortsCleanPart1';
registerRoot(()=> <Composition id="ShortsClean" component={FullFilm} width={1280} height={720} fps={30} durationInFrames={1162} defaultProps={{voiceVariant:'seedvc'}}/>);
