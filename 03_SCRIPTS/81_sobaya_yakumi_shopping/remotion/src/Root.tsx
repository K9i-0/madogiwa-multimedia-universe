import './style.css';
import {Composition} from 'remotion';
import {EditComposition} from './Composition';
import manifest from './edit-manifest.json';
import shorts from './shorts-manifest.json';
import {YakumiShorts} from './Shorts';
export const RemotionRoot: React.FC = () => <><Composition id={manifest.composition.id} component={EditComposition} width={manifest.composition.width} height={manifest.composition.height} fps={manifest.composition.fps} durationInFrames={manifest.composition.durationInFrames} /><Composition {...shorts.composition} component={YakumiShorts} /></>;
