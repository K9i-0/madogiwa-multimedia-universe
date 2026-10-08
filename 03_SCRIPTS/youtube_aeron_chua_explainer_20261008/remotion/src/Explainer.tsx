import React from 'react';
import {AbsoluteFill,Audio,Img,OffthreadVideo,Sequence,staticFile,useCurrentFrame} from 'remotion';
import m from './edit-manifest.json';
const Center:React.FC<{view:string}>=({view})=>{
 const heading=(t:string)=><div style={{fontSize:32,fontWeight:700,lineHeight:1.45,marginBottom:18}}>{t}</div>;
 const note=(t:string)=><div style={{fontSize:24,lineHeight:1.6,marginTop:16}}>{t}</div>;
 const img=(name:string,w=650,h=390)=><Img src={staticFile(name)} style={{width:w,height:h,objectFit:'contain'}}/>;
 const pair=(a:string,b:string,la:string,lb:string)=><div style={{display:'flex',gap:24,alignItems:'center'}}>{[[a,la],[b,lb]].map(([name,label])=><div key={name}>{img(name,310,310)}{note(label)}</div>)}</div>;
 if(view==='intro')return <>{heading('アーロンチュアとは何か')}{img('chair.png',420,375)}{note('高級そうな、段ボール椅子の歴史')}</>;
 if(view==='aeron')return <>{heading('アーロンチェア')}{img('aeron.jpg',400,375)}{note('Herman Miller ／ 人間工学に基づく設計')}<div style={{fontSize:14,color:'#687367',marginTop:7}}>商品画像：Herman Miller 公式サイト</div></>;
 if(view==='chair')return <>{heading('アーロンチュア')}{img('chair.png',490,410)}</>;
 if(view==='compare')return <>{heading('チェア → チュア')}{pair('aeron.jpg','chair.png','アーロンチェア','アーロンチュア')}{note('「チュア」はアクシデンチュアから')}<div style={{fontSize:14,color:'#687367',marginTop:8}}>左の商品画像：Herman Miller 公式サイト</div></>;
 if(view==='manga1'||view==='manga2')return <>{heading(view==='manga1'?'第一話「入社」':'第二話「僕の席」')}{img(view==='manga1'?'episode_01.png':'episode_02.png',450,450)}</>;
 if(view==='manga_compare')return <>{heading('席が変わっても、椅子は続投')}{pair('episode_01.png','episode_02.png','第一話「入社」','第二話「僕の席」')}</>;
 if(view==='beer')return <>{heading('入社初日')}<div style={{width:450,height:390,overflow:'hidden',position:'relative'}}><Img src={staticFile('episode_01.png')} style={{position:'absolute',width:1000,left:-280,top:-280}}/></div>{note('すでに、ビール。')}</>;
 if(view==='beer_seated')return <>{heading('椅子には、ちゃんと座っている')}{img('episode_01.png',440,440)}</>;
 if(view==='label')return <>{heading('第一話から「AERON CHUA」')}<div style={{width:430,height:365,overflow:'hidden',position:'relative'}}><Img src={staticFile('episode_01.png')} style={{position:'absolute',width:900,left:-330,top:-470}}/></div>{note('手書きの名前入り')}</>;
 if(view==='review'||view==='review_video')return <>{img(view==='review'?'episode_01.png':'seated.png',view==='review'?410:650,390)}<div style={{fontSize:38,fontWeight:700,marginTop:18}}>そば屋「快適です！」</div></>;
 if(['yotan','cto','window'].includes(view))return <div style={{display:'flex',alignItems:'center',gap:30}}><div style={{width:290,height:410,position:'relative',overflow:'hidden',background:'white'}}><Img src={staticFile('yotan.jpg')} style={{position:'absolute',width:580,maxWidth:'none',left:-95,top:-55}}/></div><div style={{width:340,textAlign:'left'}}><div style={{fontSize:43,fontWeight:700,marginBottom:26}}>よーたん</div>{view!=='yotan'&&<><div style={{fontSize:25}}>アクシデンチュア</div><div style={{fontSize:46,fontWeight:700,marginTop:5}}>CTO</div><div style={{fontSize:21,color:'#687367'}}>最高技術責任者</div></>}{view==='window'&&<div style={{fontSize:34,color:'#8d397c',marginTop:32}}>でも、窓際族。</div>}</div></div>;
 if(view==='team')return <>{heading('アーロンチュアを作る男たち')}{img('team.png')}{note('福ギュン・よーたん・そば屋')}</>;
 if(view==='assembly')return <>{heading('社員による手作り')}{img('assembly.png')}{note('採寸 → 裁断 → 組み立て')}</>;
 if(view==='lettering')return <>{heading('最後に、名前を書き入れる')}{img('lettering.png')}{note('アーロンチュア')}</>;
 if(view==='seated')return <>{heading('そば屋が着座して確認')}{img('seated.png')}</>;
 if(view==='bundle')return <>{heading('週刊 窓際を作る')}{img('bundle.png',660,410)}</>;
 if(view==='price')return <>{heading('創刊号だけで、実物大の椅子が完成')}<div style={{display:'flex',alignItems:'center',gap:24}}>{img('bundle.png',390,345)}<div style={{width:245}}><div style={{fontSize:24}}>創刊号</div><div style={{fontSize:60,fontWeight:700,color:'#8d397c'}}>399<span style={{fontSize:31}}>円</span></div>{note('材料一式付き')}</div></div></>;
 if(view==='contents'||view==='lettered_bundle')return <>{heading(view==='contents'?'段ボールの束・冊子・ガムテープ':'名前は、あらかじめ記入済み')}{img('bundle.png',660,410)}</>;
 if(view==='kitbuild')return <>{heading('やめ太郎が組み立てる')}{img('kitbuild.png')}</>;
 if(view==='mask')return <>{heading('後の号では、そば屋の仮面も')}{img('mask.png',520,365)}{note('※ 創刊号の付属品ではありません')}</>;
 if(view==='home')return <>{heading('自宅の一角が、窓際に')}{img('home.png',650,420)}</>;
 if(view==='roadmap'||view==='summary')return <>{heading('愛用品 → 社内DIY → 家庭用キット')}<div style={{display:'flex',gap:18,alignItems:'center',marginTop:25}}>{['episode_01.png','team.png','bundle.png'].map((name,i)=><React.Fragment key={name}>{i>0&&<span style={{fontSize:24}}>→</span>}<div>{img(name,180,210)}{note(['第一話','社員のDIY','創刊号399円'][i])}</div></React.Fragment>)}</div></>;
 throw new Error(`Unmapped central view: ${view}`);
};
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();const active=m.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);
 const previous=[...m.dialogue].reverse().find(d=>f>=d.startFrame);const clip=m.clips.find(c=>f>=c.startFrame&&f<c.startFrame+c.durationInFrames);const credits=f>=m.creditsStartFrame;
 return <AbsoluteFill style={{background:'#f3f0e6',fontFamily:'"Hiragino Sans", "Noto Sans JP", sans-serif',color:'#28353c'}}>
 <Audio src={staticFile('mixed.wav')}/>
 {!credits&&<>
 <div style={{position:'absolute',left:300,top:25,width:680,height:525,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',textAlign:'center'}}>
 {clip?<Sequence from={clip.startFrame} durationInFrames={clip.durationInFrames} layout="none"><OffthreadVideo muted src={staticFile(clip.src)} startFrom={clip.sourceStartFrame} style={{width:680,height:383,objectFit:'contain'}}/><div style={{fontSize:20,marginTop:14,color:'#687367'}}>{clip.label}</div></Sequence>:<Center view={previous && 'nextView' in previous && previous.nextView && f>=previous.startFrame+Math.round(previous.durationInFrames*.48)?previous.nextView:previous?.view??'intro'}/>}
 </div>
 {(['zunda','metan'] as const).map((who,i)=>{const speaking=active?.who===who;const j=active?f-active.startFrame:0;const open=speaking&&(active?.envelope[j]??0)>.023;const blink=(f+(i?49:0))%127<4;const surprise=speaking&&who==='zunda'&&/偉い|どういう|暇なの|資源ごみ|頭おかしい/.test(active?.text??'');const mood=blink?'blink':surprise?'surprise':'normal';return <Img key={who} src={staticFile(`${who}_${mood}_${Number(open)}.png`)} style={{position:'absolute',left:i?990:0,bottom:0,width:290,transform:who==='zunda'?'scaleX(-1)':undefined}}/>;})}
 {active&&<div style={{position:'absolute',left:60,right:60,bottom:27,minHeight:106,display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{fontSize:30,fontWeight:700,lineHeight:1.6,textAlign:'center',whiteSpace:'pre-line',color:active.who==='zunda'?'#347526':'#8d397c',WebkitTextStroke:'6px #fff',paintOrder:'stroke fill',textShadow:'0 2px 3px #0003'}}>{active.caption}</div></div>}
 </>}
 {credits&&<AbsoluteFill style={{alignItems:'center',justifyContent:'center',fontSize:23,lineHeight:2,textAlign:'center'}}><div>音声：VOICEVOX:ずんだもん ／ VOICEVOX:四国めたん<br/>立ち絵：坂本アヒル 様<br/>導入BGM：昼下がり気分 ／ KK<br/>本編BGM：ほのぼのワルツ【リコーダー】／ エクシエ<br/>原作・資料映像：窓際族物語</div></AbsoluteFill>}
 </AbsoluteFill>;
};
