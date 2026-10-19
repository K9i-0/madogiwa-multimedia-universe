import React from 'react';
import {AbsoluteFill,Img,OffthreadVideo,Sequence,Loop,staticFile,useCurrentFrame,interpolate} from 'remotion';
import manifest from './edit-manifest.json';
const names:Record<string,string>={sobaya:'そば屋',yametaro:'無職やめ太郎',takosan:'たこさん',fukugyun:'福ギュン',tokun:'とーくん',yotan:'よーたん',okayaman:'窓際王おかやまん',yumemin:'ゆめみん'};
const notes:Record<string,string>={sobaya:'白い仮面と、大きなジョッキ。',takosan:'黒いフードの、得体の知れない存在。',tokun:'ウクレレを奏でる、陽気な象徴社長。',yotan:'ロックを愛するCTO。',fukugyun:'笑顔で、ギュンギュン。',yametaro:'ぼやいて、逃げて、また騒動へ。',okayaman:'「大変驚いております」',yumemin:'青くて丸い、木槌の持ち主。'};
const portraits=(id:string)=>id+(id==='takosan'?'.png':'.jpg');
const ink='#263b3c',muted='#697773';
const Picture:React.FC<{src:string,w?:number,h?:number}>=({src,w=744,h=430})=><Img src={staticFile(src)} style={{width:w,height:h,objectFit:'contain'}}/>;
const Title:React.FC<{children:React.ReactNode}>=({children})=><div style={{fontSize:33,fontWeight:700,marginBottom:14,lineHeight:1.4}}>{children}</div>;
const Note:React.FC<{children:React.ReactNode}>=({children})=><div style={{fontSize:24,color:muted,marginTop:14,lineHeight:1.5}}>{children}</div>;
const Team:React.FC<{ids?:string[],title?:string}>=({ids=Object.keys(names),title='窓際族物語の8人'})=><><Title>{title}</Title><div style={{display:'grid',gridTemplateColumns:`repeat(4, 174px)`,gap:'20px 12px'}}>{ids.map(id=><div key={id}><Picture src={portraits(id)} w={174} h={ids.length===4?280:172}/><div style={{fontSize:id==='okayaman'||id==='yametaro'?20:24,fontWeight:650,marginTop:6}}>{names[id]}</div></div>)}</div></>;
const Video:React.FC<{src:string,start?:number,duration?:number,label?:string}>=({src,start=0,duration=600,label})=><><Loop durationInFrames={duration} layout="none"><OffthreadVideo muted src={staticFile(src+'.mp4')} startFrom={start} endAt={start+duration} style={{width:756,height:426,objectFit:'contain'}}/></Loop>{label&&<Note>{label}</Note>}</>;
const Person:React.FC<{id:string}>=({id})=><div style={{display:'flex',alignItems:'center',gap:25}}><Picture src={portraits(id)} w={345} h={460}/><div style={{width:370,textAlign:'left'}}><div style={{fontSize:id==='okayaman'||id==='yametaro'?37:48,fontWeight:700}}>{names[id]}</div><div style={{fontSize:25,lineHeight:1.7,marginTop:24}}>{notes[id]}</div></div></div>;
const Duo:React.FC<{ids:string[],title:string,accounts?:boolean}>=({ids,title,accounts=false})=><><Title>{title}</Title><div style={{display:'flex',gap:48}}>{ids.map((id,i)=><div key={id}><Picture src={portraits(id)} w={290} h={350}/><div style={{fontSize:28,fontWeight:700}}>{names[id]}</div>{accounts&&<div style={{fontSize:27,color:'#25726f',marginTop:10}}>{i===0?'@sobaya15':'@K9i_apps'}</div>}</div>)}</div></>;
export const Center:React.FC<{view:string}>=({view})=>{
 if(names[view])return <Person id={view}/>;
 if(/^manga[1-4]$/.test(view))return <><Picture src={view+'.png'} h={470}/><div style={{fontSize:18,color:muted,marginTop:8}}>原作漫画「窓際族物語」第{view.slice(-1)}話</div></>;
 if(['site','manga_site','videos_site','prompt_site'].includes(view))return <><Title>{view==='prompt_site'?'動画を見たら、プロンプトも。':view==='manga_site'?'漫画から始まった物語':view==='videos_site'?'気になった一本から':'公式サイトから、窓際族の世界へ'}</Title><Picture src={view+'.png'} h={380}/><div style={{fontSize:20,color:'#25726f',marginTop:10}}>madogiwa.work{view==='prompt_site'?' ／ 動画の制作ノート':''}</div></>;
 if(view==='commute'||view==='commute_callback')return <Video src="commute_intro" duration={420} label="出社インポッシブル篇"/>;
 if(view==='team')return <Team/>;
 if(view==='ending')return <><Team title="窓際族物語"/><div style={{fontSize:29,color:'#25726f',marginTop:16}}>madogiwa.work</div></>;
 if(view==='chair')return <><Title>アーロンチュア</Title><Picture src="chair.png" w={560} h={400}/><Note>本人の感想は「快適です！」</Note></>;
 if(view==='identity')return <><Team/><Note>モデルは実在。物語の役職や事件はフィクション。</Note></>;
 if(view==='realteam')return <Team ids={['tokun','yotan','fukugyun','okayaman']} title="実写の姿で登場するメンバー"/>;
 if(view==='illustrated')return <Team ids={['sobaya','takosan','yametaro','yumemin']} title="キャラクターの姿で、同じ世界へ"/>;
 if(view==='coexist')return <><Picture src="manga4.png" h={450}/><Note>実写とキャラクターが、同じ店の仲間に。</Note></>;
 if(view==='videos')return <><Title>主力コンテンツは、動画。</Title><div style={{display:'flex',gap:18}}><div><Picture src="proxy.jpg" w={355} h={210}/><Note>ニュース風</Note></div><div><Picture src="runway.jpg" w={355} h={210}/><Note>CM・コント</Note></div></div><div style={{fontSize:30,lineHeight:1.8,marginTop:24}}>日常から、ホラー、アクションまで。</div></>;
 if(view==='proxy')return <Video src="proxy" duration={870} label="替え玉出社"/>;
 if(view==='prayer')return <><Picture src="prayer.png"/><Note>デバッグ祈願 ／ 制作時の参照画像</Note></>;
 if(view==='space')return <Video src="space" duration={780} label="窓際スーパーつらい ／ 宇宙篇"/>;
 if(view==='runway')return <Video src="runway" start={120} duration={660} label="窓際族Tシャツ — 無許可のデビュー"/>;
 if(view==='workflow')return <Video src="workflow" start={2850} duration={600} label="AI動画制作の方法も紹介"/>;
 if(view==='tripo')return <Video src="tripo" start={2400} duration={600} label="キャラクターを3Dモデルにする"/>;
 if(view==='stickers_tutorial')return <Video src="stickers_tutorial" start={2850} duration={600} label="動くLINEスタンプの作り方"/>;
 if(view==='process')return <><Title>AIと一緒に、作品を作る。</Title><div style={{display:'flex',alignItems:'center',gap:20,marginTop:30}}>{['台本・参照素材','画像・映像・音声','編集・確認・修正'].map((t,i)=><React.Fragment key={t}>{i>0&&<span style={{fontSize:32,color:'#748c86'}}>→</span>}<div style={{width:185,fontSize:28,lineHeight:1.8,borderBottom:'3px solid #72a08c',paddingBottom:15}}>{t}</div></React.Fragment>)}</div><Note>できたものを見て、伝え方を考え、直していく。</Note></>;
 if(view==='reference')return <><Title>どの作品でも「この人だ」と分かるように。</Title><Picture src="reference.png" h={425}/></>;
 if(view==='tutorials')return <><Title>作品から、作り方へ。</Title><div style={{display:'flex',gap:12}}>{[['workflow','AI動画制作'],['tripo','3Dモデル'],['stickers_tutorial','動くスタンプ']].map(([id,title])=><div key={id}><Picture src={id+'.jpg'} w={240} h={190}/><div style={{fontSize:25,marginTop:14}}>{title}</div></div>)}</div><Note>実際の制作例で、手順や修正のコツを紹介。</Note></>;
 if(view==='remix')return <><Title>気に入った動画を、自分の制作の参考に。</Title><div style={{display:'flex',gap:25,alignItems:'center'}}><Picture src="sobaya.jpg" w={230} h={310}/><div style={{fontSize:40,color:'#659680'}}>→</div><Picture src="zunda_normal_0.png" w={230} h={310}/></div><Note>公開プロンプト ＋ 自分のキャラクター画像<br/>登場人物・舞台・動きを調整</Note></>;
 if(view==='games')return <><Title>同じ仲間で、ゲームも試作。</Title><div style={{display:'flex',gap:16}}>{[['escape.png','定時ダッシュ'],['quest.png','ギュンギュン・クエスト'],['card_design.png','カードの試作デザイン']].map(([src,title])=><div key={src}><Picture src={src} w={236} h={300}/><div style={{fontSize:21,marginTop:10}}>{title}</div></div>)}</div><Note>開発・試作資料 ／ 公開状況は作品ごとに異なります</Note></>;
 if(view==='ippai')return <><Title>そば屋の一杯</Title><Picture src="ippai.png" h={410}/><Note>スマホを傾けてビールを注ぐ ／ 開発・検証画面</Note></>;
 if(view==='goods')return <><Title>日常でも、窓際族と。</Title><div style={{display:'flex',gap:20}}><div><Picture src="tshirt.webp" w={360} h={300}/><Note>Tシャツ</Note></div><div><Picture src="stickers.png" w={360} h={300}/><Note>LINEスタンプ</Note></div></div></>;
 if(view==='tshirt')return <><Title>窓際族Tシャツ</Title><Picture src="tshirt.webp" h={400}/><Note>公式サイトからSUZURIへ</Note></>;
 if(view==='stickers')return <Video src="stickers" duration={90} label="会話の中にも、窓際族。"/>;
 if(view==='makers'||view==='accounts')return <Duo ids={['sobaya','takosan']} title={view==='accounts'?'制作する二人のXアカウント':'主な制作メンバー'} accounts={view==='accounts'}/>;
 if(view==='advisors')return <Duo ids={['fukugyun','yametaro']} title="アドバイザー"/>;
 throw new Error('Unknown view '+view);
};
export const Explainer:React.FC=()=>{
 const f=useCurrentFrame();const active=manifest.dialogue.find(d=>f>=d.startFrame&&f<d.startFrame+d.durationInFrames);const previous=[...manifest.dialogue].reverse().find(d=>f>=d.startFrame);const clip=manifest.clips.find(c=>f>=c.startFrame&&f<c.startFrame+c.durationInFrames);
 const fade=interpolate(f,[manifest.composition.durationInFrames-30,manifest.composition.durationInFrames-1],[1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 // Sequence begins at view change, so clips continue across consecutive dialogue lines.
 let start=0;if(previous){const index=manifest.dialogue.indexOf(previous);for(let i=index;i>=0;i--){if(manifest.dialogue[i].view!==previous.view)break;start=manifest.dialogue[i].startFrame;}if(previous.scene==='intro')start=0;}
 return <AbsoluteFill style={{background:'#f4f2eb',fontFamily:'"Hiragino Sans", "Noto Sans JP", sans-serif',color:ink}}><AbsoluteFill style={{opacity:fade}}>
 {clip?<><Sequence from={clip.startFrame} durationInFrames={clip.durationInFrames}><OffthreadVideo muted src={staticFile(clip.src)} startFrom={clip.sourceStartFrame} style={{position:'absolute',left:64,top:24,width:1152,height:648,objectFit:'contain'}}/></Sequence><div style={{position:'absolute',bottom:12,left:64,fontSize:18,color:muted}}>資料映像：{clip.label}</div></>:<>
 <Sequence from={start}><div style={{position:'absolute',left:262,top:26,width:756,height:526,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',textAlign:'center'}}><Center view={previous?.view??'commute'}/></div></Sequence>
 {(['zunda','metan'] as const).map((who,i)=>{const speaking=active?.who===who;const j=active?f-active.startFrame:0;const open=speaking&&(active?.envelope[j]??0)>.023;const blink=(f+(i?61:0))%151<4;const surprise=speaking&&/何なの|正体|社長まで|壁を壊|驚いて|不穏|登らされ|普通の出社/.test(active?.text??'');const mood=blink?'blink':surprise?'surprise':'normal';return <Img key={who} src={staticFile(`${who}_${mood}_${Number(open)}.png`)} style={{position:'absolute',left:i?1030:0,bottom:0,width:250,transform:who==='zunda'?'scaleX(-1)':undefined}}/>;})}
 {active&&<div style={{position:'absolute',left:64,right:64,bottom:30,height:112,display:'flex',alignItems:'center',justifyContent:'center'}}><div style={{fontSize:31,fontWeight:700,lineHeight:1.6,textAlign:'center',whiteSpace:'pre-line',color:active.who==='zunda'?'#347526':'#8d397c',WebkitTextStroke:'5px #fff',paintOrder:'stroke fill',textShadow:'0 2px 3px #0002'}}>{active.captions.find(c=>f-active.startFrame>=c.fromFrame&&f-active.startFrame<c.toFrame)?.text}</div></div>}
 </>}
 </AbsoluteFill></AbsoluteFill>;
};
