import React from 'react';
import {Img, staticFile, useCurrentFrame} from 'remotion';

/** Reuse only eye/mouth patches from the existing canonical commentary sprites. */
export const DuoSprite: React.FC<{who: 'yametaro'|'takosan'; speaking: boolean; open: boolean; surprise: boolean; local: number}> = ({who,speaking,open,surprise,local}) => {
  const frame=useCurrentFrame(); const tako=who==='takosan';
  const width=tako?260:245, height=width*(tako?1351/1164:1536/1024);
  const imageStyle:React.CSSProperties={position:'absolute',inset:0,width:'100%',height:'100%'};
  const patch=(name:string,mask:string)=><Img src={staticFile(`${who}_${name}.png`)} style={{...imageStyle,maskImage:mask,WebkitMaskImage:mask}}/>;
  const mouth=tako?'radial-gradient(ellipse 4.4% 2.7% at 38% 43.3%, black 75%, transparent 100%)':'radial-gradient(ellipse 5.3% 2.5% at 36.5% 47.2%, black 78%, transparent 100%)';
  return <div style={{position:'absolute',left:tako?1020:0,bottom:0,width,height,transform:`translateY(${speaking?Math.sin(local*.19)*1.2:0}px)`}}>
    <div style={{position:'absolute',inset:0,transform:tako?undefined:'scaleX(-1)'}}>
      <Img src={staticFile(`${who}_base.png`)} style={imageStyle}/>
      {tako&&(frame+23)%149<4&&patch('blink','radial-gradient(ellipse 5% 5% at 32.8% 37.6%,black 75%,transparent 100%),radial-gradient(ellipse 5.6% 5% at 49% 37.7%,black 75%,transparent 100%)')}
      {open?patch('open',mouth):surprise&&!tako?patch('surprise',mouth):null}
    </div>
  </div>;
};
