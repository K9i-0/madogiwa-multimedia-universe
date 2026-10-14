import React from 'react';
import {Composition,useCurrentFrame} from 'remotion';
import {Explainer} from './Explainer';
import {ModelScene} from './ModelScene';
import m from './edit-manifest.json';
const Demo:React.FC<{kind?:'sobaya'|'takosan'|'fukuchan';mode?:string;bones?:boolean;close?:boolean}>=({kind='sobaya',mode='turn',bones=false,close=false})=><ModelScene kind={kind} t={useCurrentFrame()/30} mode={mode} bones={bones} close={close} width={760} height={400}/>;
export const Root=()=> <><Composition id="Explainer" component={Explainer} {...m.composition}/><Composition id="ModelDemo" component={Demo} width={760} height={400} fps={30} durationInFrames={240}/></>;
