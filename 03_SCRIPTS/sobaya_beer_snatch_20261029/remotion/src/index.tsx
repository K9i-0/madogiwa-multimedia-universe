import React from 'react';
import {AbsoluteFill,Composition,Sequence,OffthreadVideo,registerRoot,staticFile} from 'remotion';
import manifest from './edit-manifest.json';
const Film=()=>{let offset=0;return <AbsoluteFill style={{background:'black'}}>{manifest.segments.map((s,i)=>{const from=offset;offset+=s.outputFrames;return <Sequence key={i} from={from} durationInFrames={s.outputFrames}><OffthreadVideo src={staticFile(`segment_${i}.mp4`)} style={{width:'100%',height:'100%'}} /></Sequence>})}</AbsoluteFill>};
registerRoot(()=> <Composition id="BeerSnatch" component={Film} width={1280} height={720} fps={manifest.fps} durationInFrames={manifest.segments.reduce((n,s)=>n+s.outputFrames,0)}/>);
