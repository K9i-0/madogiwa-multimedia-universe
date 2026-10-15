import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {ThumbnailActualV1} from './ThumbnailActualV1';
registerRoot(() => <Composition id="ThumbnailActualV1" component={ThumbnailActualV1} width={1280} height={720} fps={30} durationInFrames={1}/>);
