import React from 'react';
import {Composition} from 'remotion';
import {Explainer} from './Explainer';
import {PortraitTrial} from './PortraitTrial';
import {VoiceCandidate} from './VoiceCandidate';
import manifest from './edit-manifest.json';
import type {Manifest} from './types';
export const Root: React.FC = () => <>
  <Composition id="PortraitTrial" component={PortraitTrial} width={720} height={1280} fps={30} durationInFrames={1963}/>
  <Composition id="Explainer" component={Explainer} {...manifest.composition}/>
  <Composition id="VoiceCandidate" component={VoiceCandidate} {...manifest.composition}
    defaultProps={{manifest:manifest as Manifest,candidateLabel:'現在の採用音声（比較用props未指定）'}}
    calculateMetadata={({props})=>({...props.manifest.composition})}/>
</>;
