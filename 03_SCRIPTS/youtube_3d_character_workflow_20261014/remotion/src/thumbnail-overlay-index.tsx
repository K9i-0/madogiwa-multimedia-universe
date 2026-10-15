import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {ThumbnailOverlayV1} from './ThumbnailOverlayV1';
registerRoot(() => <Composition id="ThumbnailOverlayV1" component={ThumbnailOverlayV1} width={1280} height={720} fps={30} durationInFrames={1}/>);
