import React from 'react';
import {Composition} from 'remotion';
import {DokuChikuwa} from './Composition';
import original from './edit-manifest.json';
import natural from './edit-manifest-v5.json';
import drama from './edit-manifest-v6.json';
import tight from './edit-manifest-v7.json';
import evidence from './edit-manifest-v9.json';
import pause from './edit-manifest-v10.json';
import interior from './edit-manifest-v11.json';
import revised from './edit-manifest-v12.json';
import repaired from './edit-manifest-v13.json';
import warningUpdated from './edit-manifest-v14.json';
import proneEnding from './edit-manifest-v15.json';
import noMusic from './edit-manifest-v17.json';
import censored from './edit-manifest-v18.json';
import finished from './edit-manifest-v21.json';
import endRecordVersion from './edit-manifest-v22.json';
export const Root:React.FC=()=> <>
<Composition id="DokuChikuwa" component={DokuChikuwa} defaultProps={{manifest:original}} width={1280} height={720} fps={30} durationInFrames={original.durationInFrames}/>
<Composition id="DokuChikuwaNatural" component={DokuChikuwa} defaultProps={{manifest:natural}} width={1280} height={720} fps={30} durationInFrames={natural.durationInFrames}/>
<Composition id="DokuChikuwaDrama" component={DokuChikuwa} defaultProps={{manifest:drama,drama:true}} width={1280} height={720} fps={30} durationInFrames={drama.durationInFrames}/>
<Composition id="DokuChikuwaTight" component={DokuChikuwa} defaultProps={{manifest:tight,drama:true}} width={1280} height={720} fps={30} durationInFrames={tight.durationInFrames}/>
<Composition id="DokuChikuwaRecords" component={DokuChikuwa} defaultProps={{manifest:tight,drama:true,records:true}} width={1280} height={720} fps={30} durationInFrames={tight.durationInFrames}/>
<Composition id="DokuChikuwaEvidence" component={DokuChikuwa} defaultProps={{manifest:evidence,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={evidence.durationInFrames}/>
<Composition id="DokuChikuwaPause" component={DokuChikuwa} defaultProps={{manifest:pause,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={pause.durationInFrames}/>
<Composition id="DokuChikuwaInterior" component={DokuChikuwa} defaultProps={{manifest:interior,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={interior.durationInFrames}/>
<Composition id="DokuChikuwaRevised" component={DokuChikuwa} defaultProps={{manifest:revised,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={revised.durationInFrames}/>
<Composition id="DokuChikuwaRepaired" component={DokuChikuwa} defaultProps={{manifest:repaired,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={repaired.durationInFrames}/>
<Composition id="DokuChikuwaWarningUpdated" component={DokuChikuwa} defaultProps={{manifest:warningUpdated,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={warningUpdated.durationInFrames}/>
<Composition id="DokuChikuwaProneEnding" component={DokuChikuwa} defaultProps={{manifest:proneEnding,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={proneEnding.durationInFrames}/>
<Composition id="DokuChikuwaNoMusic" component={DokuChikuwa} defaultProps={{manifest:noMusic,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={noMusic.durationInFrames}/>
<Composition id="DokuChikuwaMosaic" component={DokuChikuwa} defaultProps={{manifest:censored,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={censored.durationInFrames}/>
<Composition id="DokuChikuwaFinished" component={DokuChikuwa} defaultProps={{manifest:finished,drama:true,records:true,enhanced:true}} width={1280} height={720} fps={30} durationInFrames={finished.durationInFrames}/>
<Composition id="DokuChikuwaFinalRecord" component={DokuChikuwa} defaultProps={{manifest:endRecordVersion,drama:true,records:true,enhanced:true,endRecord:true}} width={1280} height={720} fps={30} durationInFrames={endRecordVersion.durationInFrames}/>
</>;
