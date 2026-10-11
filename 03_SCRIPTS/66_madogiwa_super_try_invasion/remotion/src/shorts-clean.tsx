import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {Full} from './ShortsCleanFilm';
import m from './shorts-clean-manifest.json';
registerRoot(()=> <Composition id="ShortsClean" component={Full} {...m.composition} defaultProps={{preview:false}}/>);
