import {Composition,registerRoot} from 'remotion';
import {EditComposition} from './Composition';
import raw from './shorts-clean-manifest.json';
import type {EditManifest} from './types';
const manifest=raw as EditManifest;
registerRoot(()=> <Composition id="ShortsClean" component={EditComposition} width={manifest.composition.width} height={manifest.composition.height} fps={manifest.composition.fps} durationInFrames={manifest.composition.durationInFrames} defaultProps={{manifest}}/>);
