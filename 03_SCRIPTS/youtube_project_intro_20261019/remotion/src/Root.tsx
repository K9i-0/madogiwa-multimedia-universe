import React from 'react';
import {Composition} from 'remotion';
import {Explainer} from './Explainer';
import manifest from './edit-manifest.json';
export const Root:React.FC=()=> <Composition id="ProjectIntro" component={Explainer} {...manifest.composition}/>;
