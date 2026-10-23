import React from 'react';
import {Composition} from 'remotion';
import {Film} from './Film';
import {Short} from './Short';
import shorts from './shorts-manifest.json';
import manifest from './edit-manifest.json';
export const Root = () => <><Composition id="MDECrosstech" component={Film} width={1280} height={720} fps={30} durationInFrames={manifest.composition.durationInFrames}/><Composition id="MDEShort" component={Short} width={720} height={1280} fps={30} durationInFrames={shorts.durationInFrames}/></>;
