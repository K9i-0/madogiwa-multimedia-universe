import React from 'react';
import {AbsoluteFill,Audio,Img,OffthreadVideo,Sequence,staticFile,useCurrentFrame,interpolate} from 'remotion';
import m from './edit-manifest.json';
import views from './views.json';
const gold='#c9b682';
const imageViews:Record<string,string>={habitat_window:'window',identity:'sobaya',space_question:'spacebeer',sobaya:'sobaya',beer:'beer',window:'window',jungle:'jungle',ritual:'ritual',waiting:'waiting',offering:'offering',captives:'captives',capture:'capture',earth:'earth',approach:'approach',swim:'swim',spacebeer:'spacebeer',lab:'lab',tanks:'tanks',researcher:'researcher',pursuit:'pursuit'};
const movies:Record<string,[string,number]>={jungle:['jungle_motion',180],swim:['swim_motion',180],capture:['capture_motion',210],lab:['lab_motion',180]};
const Heading:React.FC<{children:React.ReactNode}>=({children})=><div style={{fontSize:30,letterSpacing:2,lineHeight:1.5,marginBottom:18,fontFamily:'"Hiragino Mincho ProN",serif'}}>{children}</div>;
const Panel:React.FC<{view:string;elapsed:number;start:number}>=({view,elapsed,start})=>{
 const v=views[view as keyof typeof views];const img=imageViews[view];const film=movies[view];
 const photo=(name:string,width=780,height=366)=><Img src={staticFile(`${name}.jpg`)} style={{width,height,objectFit:'contain'}}/>;
 const box=(t:string,small?:string)=><div style={{borderTop:`1px solid ${gold}66`,padding:'20px 14px',minWidth:170}}><div style={{fontSize:32,color:gold,whiteSpace:'pre-line'}}>{t}</div>{small&&<div style={{fontSize:20,marginTop:12,color:'#b4bec3',lineHeight:1.6}}>{small}</div>}</div>;
 if(view==='title')return <><div style={{fontSize:17,letterSpacing:7,color:gold,marginBottom:35}}>未知を、記録する。</div><div style={{fontFamily:'"Hiragino Mincho ProN",serif',fontSize:54,lineHeight:1.7}}>めたんの<br/>ミステリー研究所</div><div style={{width:100,height:1,background:gold,margin:'30px auto'}}/></>;
 return <><Heading>{v.heading}</Heading>
 {img&&<div style={{height:366,width:780,position:'relative',overflow:'hidden',display:'flex',alignItems:'center',justifyContent:'center'}}>
 {film&&elapsed<film[1]?<Sequence from={start} durationInFrames={film[1]} layout="none"><OffthreadVideo muted src={staticFile(`${film[0]}.mp4`)} style={{width:780,height:366,objectFit:'contain'}}/></Sequence>:<div style={{transform:`scale(${1+Math.min(elapsed,1000)*.000035})`}}>{photo(img)}</div>}
 {(view==='window'||view==='habitat_window')&&<div style={{position:'absolute',right:140,top:15,width:245,height:275,border:'2px solid #c9b68299'}}/>}
 {view==='waiting'&&<div style={{position:'absolute',bottom:20,right:35,fontSize:66,textShadow:'0 2px 12px black',fontFamily:'serif'}}>三年</div>}
 </div>}
 {view==='exchange'&&<div style={{height:366,display:'flex',alignItems:'center',gap:25}}>{box('一本','本数を確認')}<span style={{fontSize:34}}>→</span>{box('一箱','着席を許可')}</div>}
 {view==='choice'&&<div style={{height:366,display:'flex',alignItems:'center',gap:35}}>{box('仲間になる','集団への加入')}<span style={{fontSize:22}}>または</span>{box('ギュンされる','具体的な処置は不明')}</div>}
 {view==='exchange_space'&&<div style={{height:366,display:'flex',alignItems:'center',gap:24}}><div>{photo('offering',365,240)}{box('地上：受け取る')}</div><div>{photo('spacebeer',365,240)}{box('宇宙：差し出す')}</div></div>}
 {view==='comparison'&&<div style={{height:366,display:'flex',alignItems:'center',gap:24}}><div>{photo('sobaya',365,240)}{box('原個体','指示への反応に難点')}</div><div>{photo('pursuit',365,240)}{box('複製個体','指示後に行動を開始')}</div></div>}
 {view==='summary'&&<div style={{height:366,display:'flex',flexDirection:'column',justifyContent:'center',gap:16,width:660}}>{['01　窓の近くに現れる','02　長期間、待ち続ける','03　ビールを受け取り、差し出す','04　群れに加入を迫る','05　指示に従うと、違和感がある'].map(t=><div key={t} style={{fontSize:27,textAlign:'left',padding:'8px 20px',borderBottom:'1px solid #c9b68233'}}>{t}</div>)}</div>}
 {view==='archive'&&<div style={{height:366,display:'flex',flexDirection:'column',justifyContent:'center',gap:28}}><div style={{fontSize:20,letterSpacing:6,color:gold}}>分類再検討資料</div><div style={{fontSize:64,fontFamily:'serif'}}>人事部への照会</div><div style={{fontSize:21,color:'#a4b0b8'}}>映像の分析から、在籍情報の照合へ</div></div>}
 {view==='answer'&&<div style={{height:366,display:'flex',alignItems:'center',fontSize:66,fontFamily:'serif',color:gold}}>「うちの社員です」</div>}
 {view==='employee'&&<div style={{height:366,display:'flex',alignItems:'center',gap:25}}>{photo('sobaya',390,320)}<div style={{textAlign:'left'}}><div style={{fontSize:23}}>アクシデンチュア</div><div style={{fontSize:55,color:gold,margin:'20px 0'}}>窓際社員</div><div style={{fontSize:24}}>そば屋</div></div></div>}
 {view==='reinterpret'&&<div style={{height:366,display:'flex',flexDirection:'column',justifyContent:'center',gap:30,fontSize:31}}><div>生息域「マドギワ」　→　窓際の席</div><div>三年に及ぶ待機　→　アサイン待ち</div><div>反復される発声　→　アベイラブル</div></div>}
 {view==='closing'&&<div style={{height:366,display:'flex',alignItems:'center',justifyContent:'center',fontSize:40,lineHeight:1.9,fontFamily:'serif'}}>生態の解明は、<br/>今後の課題である。</div>}
 <div style={{fontSize:19,color:'#b0babd',marginTop:17,lineHeight:1.5}}>{v.note}</div></>;
};
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);const idx=m.dialogue.reduce((found,d,i)=>f>=d.startFrame?i:found,-1);const previous=m.dialogue[Math.max(idx,0)];const view=previous.view;
 let first=Math.max(idx,0);while(first>0&&m.dialogue[first-1].view===view)first--;const start=m.dialogue[first].startFrame;const elapsed=Math.max(0,f-start);const credits=f>=m.creditsStartFrame;
 const openingSilence=idx===2&&!active;
 return <AbsoluteFill style={{background:'#0b1118',fontFamily:'"Hiragino Sans",sans-serif',color:'#e6e5df'}}>
 <Audio src={staticFile('mixed.wav')}/>
 <AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 30%, #23303988 0%, #091018 78%)'}}/>
 {view==='title'&&<AbsoluteFill style={{opacity:.13}}><Img src={staticFile('forest.png')} style={{width:'100%',height:'100%',objectFit:'cover'}}/></AbsoluteFill>}
 {!credits&&<>
 <div style={{position:'absolute',left:240,top:38,width:800,height:500,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',textAlign:'center',opacity:openingSilence?interpolate(f-(previous.startFrame+previous.durationInFrames),[55,95],[1,.15],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}):1}}><Panel view={view} elapsed={elapsed} start={start}/></div>
 {(['zunda','metan'] as const).map((who,i)=>{const speaking=active?.who===who;const j=active?f-active.startFrame:0;const open=speaking&&(active?.envelope[j]??0)>.025;const blink=(f+(i?49:0))%137<4;const surprise=speaking&&who==='zunda'&&/最悪|卑しい|出来悪い|社員だった|まとめて|信用できない/.test(active?.text??'');const mood=blink?'blink':surprise?'surprise':'normal';return <Img key={who} src={staticFile(`${who}_${mood}_${Number(open)}.png`)} style={{position:'absolute',left:i?1050:0,bottom:52,width:230,transform:who==='zunda'?'scaleX(-1)':undefined,filter:speaking?'none':'brightness(.86)'}}/>;})}
 {active&&<div style={{position:'absolute',left:52,right:52,bottom:28,minHeight:111,background:'#091018ef',borderTop:`1px solid ${active.who==='zunda'?'#9bbd7955':'#d6a1cc55'}`,display:'flex',alignItems:'center',justifyContent:'center',padding:'8px 12px'}}><div style={{fontSize:28,fontWeight:500,lineHeight:1.65,textAlign:'center',whiteSpace:'pre-line',color:active.who==='zunda'?'#cae6ab':'#f0c9e7'}}>{active.caption}</div></div>}
 </>}
 {credits&&<AbsoluteFill style={{alignItems:'center',justifyContent:'center',textAlign:'center',opacity:interpolate(f,[m.composition.durationInFrames-45,m.composition.durationInFrames],[1,0],{extrapolateLeft:'clamp'})}}><div style={{fontSize:32,fontFamily:'serif',marginBottom:35}}>めたんのミステリー研究所</div><div style={{fontSize:22,lineHeight:2}}>音声：VOICEVOX:四国めたん ／ VOICEVOX:ずんだもん<br/>立ち絵：坂本アヒル<br/>原作・資料映像：窓際族物語<br/>音楽：本作オリジナル・アンビエント</div><div style={{fontSize:17,color:'#a4afb8',lineHeight:1.8,marginTop:30}}>本番組はフィクションです。研究史・人事照会は解説用の再構成です。<br/>資料映像：密林のアベイラブル／マドギワ族の秘密<br/>宇宙カジュアル篇／そば屋クローン研究所</div></AbsoluteFill>}
 </AbsoluteFill>;
};
