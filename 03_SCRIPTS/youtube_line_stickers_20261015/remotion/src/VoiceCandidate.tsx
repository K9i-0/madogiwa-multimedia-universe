import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Explainer} from './Explainer';
import type {Manifest} from './types';

export type VoiceCandidateProps = {
  manifest: Manifest;
  candidateLabel: string;
};

/** Audition only: the canonical manifest and adopted voices are never replaced. */
export const VoiceCandidate: React.FC<VoiceCandidateProps> = ({manifest, candidateLabel}) => (
  <AbsoluteFill>
    <Explainer manifest={manifest} />
    <div style={{position:'absolute',right:18,top:39,height:26,padding:'0 10px',
      display:'flex',alignItems:'center',borderRadius:3,background:'#edf5ff',
      color:'#204b72',fontFamily:'"Hiragino Sans",sans-serif',fontSize:16,fontWeight:600}}>
      やめ太郎の声：{candidateLabel}
    </div>
  </AbsoluteFill>
);
