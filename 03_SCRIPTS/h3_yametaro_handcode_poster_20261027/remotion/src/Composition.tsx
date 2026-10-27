import React from 'react';
import {AbsoluteFill, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {Video} from '@remotion/media';
import manifest from './edit-manifest.json';
import transformsJson from './face-transforms.json';
const transforms = transformsJson as Record<string, number[][]>;
const AnimatedMouth: React.FC<{chapter: typeof manifest.chapters[number]}> = ({chapter: ch}) => {
  const frame=useCurrentFrame()+ch.sourceStart;
  const key=ch.file.replace('_480p.mp4','');
  const matrix=transforms[key][Math.min(frame,transforms[key].length-1)];
  const [a,c,e,b,d,f]=matrix;
  const scale=manifest.composition.width/480;
  const {cx,cy,rx,ry} = manifest.faceMask;
  const mask = `radial-gradient(ellipse ${rx}px ${ry}px at ${cx}px ${cy}px, black 72%, transparent 100%)`;
  return <AbsoluteFill style={{WebkitMaskImage:mask, maskImage:mask}}>
    <Video src={staticFile(ch.file)} trimBefore={ch.sourceStart} muted
      style={{width:'100%',height:'100%',transformOrigin:'0 0',
        transform:`matrix(${a},${b},${c},${d},${e*scale},${f*scale})`}} objectFit="fill" />
  </AbsoluteFill>;
};
export const EditComposition: React.FC = () => <AbsoluteFill style={{backgroundColor:'#e5b119'}}>
  <Img src={staticFile(manifest.poster)} style={{width:'100%',height:'100%'}} />
  {manifest.chapters.map(ch => <Sequence key={ch.id} from={ch.from} durationInFrames={ch.frames}>
    <AnimatedMouth chapter={ch} />
  </Sequence>)}
</AbsoluteFill>;
