import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {Production} from './ShortsCleanFilm';
import m from './shorts-clean-manifest.json';
registerRoot(()=> <Composition id="ShortsClean" component={Production} {...m.composition} defaultProps={{preview:false}}/>);
