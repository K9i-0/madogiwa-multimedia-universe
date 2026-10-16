import React from 'react';
import {Img, staticFile, useCurrentFrame} from 'remotion';
export type Mood='normal'|'happy'|'surprise'|'worry'|'bored'|'angry'|'sad'|'smug';
/** Canonical full expression/pose exports; the canvas and foot position stay fixed. */
export const DuoSprite: React.FC<{who: 'yametaro'|'takosan'; speaking: boolean; open: boolean; mood:Mood; local: number; portrait?:boolean}> = ({who,speaking,open,mood,local,portrait=false}) => {
 const frame=useCurrentFrame();const tako=who==='takosan';
 const width=tako?260:245,height=width*(tako?1351/1164:1536/1024);
 const style:React.CSSProperties={position:'absolute',inset:0,width:'100%',height:'100%'};
 const blink=tako&&mood==='normal'&&(frame+23)%149<4;
 const mask='radial-gradient(ellipse 5.4% 5% at 32.8% 37.6%,black 80%,transparent 100%),radial-gradient(ellipse 5.8% 5% at 49% 37.7%,black 80%,transparent 100%)';
 return <div style={{position:'absolute',left:portrait?(tako?426:64):(tako?1020:0),bottom:portrait?265:35,width:portrait?width*.86:width,height:portrait?height*.86:height,transform:`translateY(${speaking?Math.sin(local*.19)*1.2:0}px)`}}><div style={{position:'absolute',inset:0,transform:tako?undefined:'scaleX(-1)'}}>
  <Img src={staticFile(`expressions/${who}_${mood}_${open?'open':'closed'}.png`)} style={style}/>
  {blink&&<Img src={staticFile('takosan_blink.png')} style={{...style,maskImage:mask,WebkitMaskImage:mask}}/>}
 </div></div>;
};
