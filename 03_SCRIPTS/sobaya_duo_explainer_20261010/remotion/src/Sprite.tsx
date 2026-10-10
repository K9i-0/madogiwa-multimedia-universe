import React from 'react';
import {Img,staticFile} from 'remotion';
export const moods=['normal','happy','surprise','worry','bored','angry','sad','smug'] as const;
export type Mood=typeof moods[number];
export type Who='takosan'|'yametaro';
export const Sprite:React.FC<{who:Who;mood:Mood;open?:boolean;blink?:boolean;mirror?:boolean}>=({who,mood,open=false,blink=false,mirror=false})=>{
 const tako=who==='takosan';const css:React.CSSProperties={position:'absolute',inset:0,width:'100%',height:'100%'};
 const patch=(name:string,mask:string)=><Img src={staticFile(`sprites/${who}_${name}.png`)} style={{...css,maskImage:mask,WebkitMaskImage:mask}}/>;
 const mouth=tako?'radial-gradient(ellipse 5.4% 3.8% at 40.5% 43.2%,black 78%,transparent 100%)':'radial-gradient(ellipse 6% 3.2% at 36.6% 47.2%,black 78%,transparent 100%)';
 return <div style={{position:'absolute',inset:0,transform:mirror?'scaleX(-1)':undefined}}>
  <Img src={staticFile(`sprites/${who}_${mood}.png`)} style={css}/>
  {tako&&blink&&mood!=='happy'&&patch('blink','radial-gradient(ellipse 5.4% 5% at 32.8% 37.6%,black 80%,transparent 100%),radial-gradient(ellipse 5.8% 5% at 49% 37.7%,black 80%,transparent 100%)')}
  {open?patch(!tako&&['surprise','worry','bored','angry','sad'].includes(mood)?'mouth_round':'mouth_open',mouth):mood==='surprise'?patch('normal',mouth):null}
 </div>;
};
