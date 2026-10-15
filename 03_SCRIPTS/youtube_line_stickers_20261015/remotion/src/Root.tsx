import React from 'react';
import {Composition} from 'remotion';
import {Explainer} from './Explainer';
import {VoiceCandidate} from './VoiceCandidate';
import manifest from './edit-manifest.json';
import type {Manifest} from './types';
export const Root: React.FC = () => <>
  <Composition id="Explainer" component={Explainer} {...manifest.composition}/>
  <Composition id="VoiceCandidate" component={VoiceCandidate} {...manifest.composition}
    defaultProps={{manifest:manifest as Manifest,candidateLabel:'現行 Irodori'}}
    calculateMetadata={({props})=>({...props.manifest.composition})}/>
</>;
