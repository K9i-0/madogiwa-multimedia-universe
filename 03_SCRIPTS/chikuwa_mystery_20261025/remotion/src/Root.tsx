import React from 'react';
import {Composition} from 'remotion';
import {Explainer} from './Explainer';
import m from './edit-manifest.json';
export const Root:React.FC=()=> <Composition id="Explainer" component={Explainer} {...m.composition}/>;
