import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {ThumbnailModelV1} from './ThumbnailModelV1';

/** Actual source pixels and canonical GLB under the imagegen foreground only. */
export const ThumbnailOverlayV1 = () => <AbsoluteFill style={{background:'#f3eee5'}}>
  <div style={{position:'absolute',left:640,top:105,width:640,height:615,overflow:'hidden',background:'#263831'}}>
    <div style={{position:'absolute',left:-190,top:30}}>
      <ThumbnailModelV1 kind="sobaya" mode="turn" t={2.8} freeze width={830} height={560} zoom={1.14}/>
    </div>
  </div>
  <div style={{position:'absolute',left:185,top:113,width:430,height:607,overflow:'hidden'}}>
    <Img src={staticFile('sobaya_reference_v4.png')} style={{position:'absolute',width:1805.76,height:1016.28,maxWidth:'none',left:0,top:-119}}/>
  </div>
  <div style={{position:'absolute',left:0,right:0,top:0,height:116,background:'linear-gradient(#fff 78%,#fff0)'}}/>
  <Img src={staticFile('thumbnail_foreground_v1.png')} style={{position:'absolute',inset:0,width:1280,height:720}}/>
</AbsoluteFill>;
