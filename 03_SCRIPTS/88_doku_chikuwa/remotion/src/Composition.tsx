import React from 'react';
import {AbsoluteFill,Audio,Img,OffthreadVideo,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import originalManifest from './edit-manifest.json';
type Props={manifest:typeof originalManifest;drama?:boolean;records?:boolean;enhanced?:boolean;endRecord?:boolean};
export const DokuChikuwa:React.FC<Props>=({manifest,drama=false,records=false,enhanced=false,endRecord=false})=> <AbsoluteFill style={{backgroundColor:'#000'}}>
 {manifest.shots.map((s,i)=><Sequence key={i} from={s.from} durationInFrames={s.duration}>
  <Shot shot={s} drama={drama} enhanced={enhanced} endClose={records&&i===manifest.shots.length-1}/>
 </Sequence>)}
 {drama&&<DramaOverlay records={records} manifest={manifest} endRecord={endRecord}/>}
 <Audio src={staticFile(manifest.audio)}/>
</AbsoluteFill>;

const DramaOverlay:React.FC<{records:boolean;manifest:typeof originalManifest;endRecord:boolean}>=({records,manifest,endRecord})=>{
 const f=useCurrentFrame();
 const opacity=interpolate(f,[8,23,87,103],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 const evidence1=manifest.shots[1];const evidence2=manifest.shots[2];
 const a=evidence1.from,b=a+evidence1.duration,c=evidence2.from,d=c+evidence2.duration;
 const last=manifest.shots[manifest.shots.length-1];
 const ending=endRecord&&f>=last.from&&f<last.from+last.duration?{start:last.from,end:last.from+last.duration,title:'現場記録③　毒ちくわ',body:'そば屋のつまみ食いにより判明'}:null;
 const record=ending??(records?(f>=a&&f<b?{start:a,end:b,title:'現場記録①　夕食のおでん',body:'ちくわに紫色の変色を確認'}:f>=c&&f<d?{start:c,end:d,title:'現場記録②　被害者が残した血文字',body:'「ちくわ」と読める文字を確認'}:null):null);
 const recordOpacity=record?interpolate(f,[record.start,record.start+10,record.end-10,record.end],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}):0;
 return <AbsoluteFill style={{pointerEvents:'none'}}>
 <AbsoluteFill style={{background:'rgba(22,44,72,.055)',mixBlendMode:'color'}}/>
 <AbsoluteFill style={{background:'radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.16) 100%)'}}/>
 {f<107&&<div style={{position:'absolute',left:66,bottom:55,color:'#f1f0ec',fontFamily:'"Hiragino Mincho ProN",serif',textShadow:'0 2px 6px #000',opacity,letterSpacing:3}}>
 <div style={{fontSize:28}}>東京都港区赤坂</div><div style={{fontSize:21,marginTop:10}}>午後8時14分</div>
 </div>}
 {record&&<div style={{position:'absolute',left:66,bottom:55,color:'#f1f0ec',fontFamily:'"Hiragino Mincho ProN",serif',textShadow:'0 2px 6px #000',opacity:recordOpacity,letterSpacing:3}}>
 <div style={{fontSize:28}}>{record.title}</div><div style={{fontSize:21,marginTop:10}}>{record.body}</div>
 </div>}
 </AbsoluteFill>;
};

const Shot:React.FC<{shot:typeof originalManifest.shots[number];drama:boolean;enhanced:boolean;endClose:boolean}>=({shot:s,drama,enhanced,endClose})=>{
 const frame=useCurrentFrame();
 let scale=endClose?1.85:1;
 let origin=endClose?'48% 53%':'50% 50%';
 if(enhanced&&!endClose&&s.kind==='image'&&s.file.endsWith('_v9.png')){
  scale=interpolate(frame,[0,s.duration-1],[1,1.045],{extrapolateRight:'clamp'});
  origin=s.from===730?'64% 53%':'50% 50%';
 }
 // Hide the old unmarked floor in the retained two-person dialogue shots.
 if(enhanced&&s.kind==='video'&&s.file==='wan3_result_v2_480p.mp4'&&(s.sourceStart===165||s.sourceStart===453)){scale=1.25;origin='45% 0%';}
 if(s.file==='wan3_interior_v11_480p.mp4'&&s.from===597){scale=1.4;origin='35% 0%';}
 if(s.file==='wan3_interior_v11_480p.mp4'&&s.from===900){scale=1.6;origin='40% 0%';}
 if(s.file==='wan3_collapse_v11_480p.mp4'){scale=2;origin='0% 100%';}
 const style:React.CSSProperties={width:'100%',height:'100%',objectFit:'cover',transform:`scale(${scale})`,transformOrigin:origin,filter:drama?'saturate(.88) contrast(1.035) brightness(.98)':undefined};
 return <AbsoluteFill style={{overflow:'hidden'}}>{s.kind==='video'?<OffthreadVideo src={staticFile(s.file)} startFrom={s.sourceStart} muted style={style}/>:<Img src={staticFile(s.file)} style={style}/>}</AbsoluteFill>;
};
