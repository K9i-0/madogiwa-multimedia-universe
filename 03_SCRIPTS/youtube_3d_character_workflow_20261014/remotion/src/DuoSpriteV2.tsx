import React from 'react';
import {Img,staticFile,useCurrentFrame} from 'remotion';
import {Mood} from './DuoSprite';
export function DuoSpriteV2({who,speaking,open,mood,local}:{who:'yametaro'|'takosan';speaking:boolean;open:boolean;mood:Mood;local:number}){
 const frame=useCurrentFrame(),tako=who==='takosan';const width=tako?158:146,height=width*(tako?1351/1164:1536/1024);const blink=tako&&mood==='normal'&&(frame+23)%149<4;
 const style:React.CSSProperties={position:'absolute',inset:0,width:'100%',height:'100%'};
 const mask='radial-gradient(ellipse 5.4% 5% at 32.8% 37.6%,black 80%,transparent 100%),radial-gradient(ellipse 5.8% 5% at 49% 37.7%,black 80%,transparent 100%)';
 return <div style={{position:'absolute',left:tako?1122:16,bottom:35,width,height,transform:`translateY(${speaking?Math.sin(local*.12)*.6:0}px)`}}><div style={{position:'absolute',inset:0,transform:tako?undefined:'scaleX(-1)'}}><Img src={staticFile(`expressions/${who}_${mood}_${open?'open':'closed'}.png`)} style={style}/>{blink&&<Img src={staticFile('takosan_blink.png')} style={{...style,maskImage:mask,WebkitMaskImage:mask}}/>}</div></div>;
}
