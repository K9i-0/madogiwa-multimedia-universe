import React from 'react';
import {Composition} from 'remotion';
import {Film} from './Film';
import manifest from './edit-manifest.json';
export const Root = () => <Composition id="MDECrosstech" component={Film} width={1280} height={720} fps={30} durationInFrames={manifest.composition.durationInFrames}/>;
