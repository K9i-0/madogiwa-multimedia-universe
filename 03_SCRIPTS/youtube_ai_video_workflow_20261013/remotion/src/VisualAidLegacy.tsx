import React from 'react';
import cues from './visual-cues-v6.json';
import {Img, staticFile, interpolate} from 'remotion';

// Visuals follow the adopted narration. All cue positions resolve to integer frames.
type Utterance = {id?:string; startFrame:number; durationInFrames:number};
const green='#438255', purple='#95527e', ink='#263e44', grey='#61716d';
const Pic=({name,w=700,h=370}:{name:string;w?:number;h?:number})=><Img src={staticFile(name)} style={{width:w,height:h,objectFit:'contain'}}/>;
const Head=({children}:{children:React.ReactNode})=><div style={{fontSize:32,fontWeight:700,marginBottom:28,lineHeight:1.4}}>{children}</div>;
const Big=({children}:{children:React.ReactNode})=><div style={{fontSize:46,fontWeight:700,lineHeight:1.6,color:green}}>{children}</div>;
const Small=({children}:{children:React.ReactNode})=><div style={{fontSize:18,color:grey,marginTop:18,lineHeight:1.5}}>{children}</div>;
const Row=({children}:{children:React.ReactNode})=><div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:22,width:710}}>{children}</div>;
const Arrow=()=> <span style={{color:'#9ba99c',fontSize:32}}>→</span>;
const Tile=({children,active=true,show=true}:{children:React.ReactNode;active?:boolean;show?:boolean})=><div style={{flex:1,padding:'22px 13px',borderRadius:14,background:active?'#e2ebdf':'#ecece5',color:active?ink:grey,opacity:show?(active?1:.38):0,fontSize:27,fontWeight:600,lineHeight:1.6,borderBottom:`4px solid ${active?green:'transparent'}`}}>{children}</div>;
const Pair=({a,b,al,bl,focus=-1}:{a:string;b:string;al:string;bl:string;focus?:number})=><Row>{[a,b].map((name,i)=><div key={name} style={{opacity:focus<0||focus===i?1:.35}}><Pic name={name} w={342} h={300}/><div style={{fontSize:24,marginTop:18,color:i?purple:green}}>{[al,bl][i]}</div></div>)}</Row>;
const Crop=({part}:{part:'face'|'body'})=><div style={{width:part==='face'?305:176,height:part==='face'?282:370,overflow:'hidden',position:'relative',background:'white',borderRadius:8}}><Img src={staticFile('fuku_sheet.png')} style={part==='face'?{position:'absolute',width:850,maxWidth:'none',left:-545,top:0}:{position:'absolute',height:370,maxWidth:'none',left:0,top:0}}/></div>;
const Workflow=({stage,reached=stage,complete=false}:{stage:number;reached?:number;complete?:boolean})=><div style={{width:710}}>
  <div style={{fontSize:25,marginBottom:22,color:grey}}>作りたいこと</div>
  <div style={{fontSize:27,color:'#9ba99c',marginBottom:14}}>↓</div>
  <div style={{opacity:complete||stage===0?1:.4,background:'#e2ebdf',padding:20,borderRadius:14,fontSize:31,fontWeight:700,color:green}}>Codex / Claude Code</div>
  <div style={{fontSize:27,color:'#9ba99c',margin:'12px 0',opacity:reached>0?1:0}}>↓</div>
  <Row>{['Wan 3.0','Irodori','Remotion'].map((x,i)=><React.Fragment key={x}>{i>0&&<span style={{opacity:complete||i+1<=reached?1:0}}><Arrow/></span>}<Tile active={complete||stage===i+1} show={complete||i+1<=reached}><span style={{fontSize:27}}>{x}</span><div style={{fontSize:20,marginTop:8,fontWeight:400}}>{['映像＋声','必要な声を修正','字幕・編集'][i]}</div></Tile></React.Fragment>)}</Row>
</div>;

export const VisualAid:React.FC<{view:string;frame:number;utterance?:Utterance;cueOverride?:Record<string,number>}>=({view,frame,utterance,cueOverride})=>{
 const id=utterance?.id??'n000';
 const f=frame-(utterance?.startFrame??0), dur=utterance?.durationInFrames??100;
 const timing=cueOverride??{};
 const cue=(ratio:number)=>timing[String(ratio)]??Math.round(dur*ratio);
 const at=(ratio:number)=>f>=cue(ratio);
 const phase=(cuts:number[])=>cuts.filter(at).length;
 const reveal=(ratio:number)=>interpolate(f,[cue(ratio),cue(ratio)+8],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 if(view==='hook_wish')return <>
   {['n000','n001'].includes(id)?<><div style={{fontSize:80,color:green,marginBottom:20}}>▷</div><Big>動画も、作りたい。</Big></>:<><div style={{display:'flex',gap:12,alignItems:'flex-end',height:170}}>{[80,135,105,165,120].map((h,i)=><div key={i} style={{width:65,height:h,background:'#dce7d9',borderRadius:'9px 9px 0 0'}}/>)}</div><Head>しょうもない話なら、山ほど。</Head>{id==='n003'&&<div style={{fontSize:30,color:purple}}>いい話は？</div>}{id==='n004'&&<div style={{opacity:reveal(.45),fontSize:38,color:purple}}>0 本</div>}</>}
 </>;
 if(view==='hook_barrier')return <><Row><Tile active={id==='n005'}>Web・アプリ<br/><span style={{fontSize:48,color:green}}>✓</span></Tile><Arrow/><Tile active={id!=='n005'}>動画編集<br/><span style={{fontSize:48,color:purple}}>？</span></Tile></Row>{id==='n008'&&<div style={{fontSize:28,marginTop:35}}>ネタ ✓　やる気 ✓　操作 ？</div>}</>;
 if(view==='hook_bridge')return <>{['n024','n025','n026'].includes(id)?<Row><Tile active={id==='n024'}>アイデア</Tile><Arrow/><Tile active={id!=='n024'}>見て、直す</Tile></Row>:<><Big>Codex / Claude Code</Big><div style={{fontSize:29,marginTop:32,padding:'20px 35px',borderRadius:25,background:'white'}}>「ここ直して」</div></>}</>;
 if(view==='intro_ready'||view==='opening')return <><Head>いつものAIから</Head><Big>動画まで作る。</Big><Small>窓際族物語の実例</Small></>;
 if(view==='intro_reaction'||view==='promise')return <Pic name="news.jpg" h={430}/>;
 if(view==='hook_agenda'){const step=id==='n029'?3:phase([.33,.55,.74])-1;return <><Head>今日、持ち帰ること</Head><div style={{width:670,display:'grid',gridTemplateColumns:'1fr 1fr',gap:22}}>{['作る道具','かかるお金','失敗の直し方','次に残す手順'].map((x,i)=><Tile key={x} active={i===step} show={i<=step}>{x}</Tile>)}</div></>;}
 if(view==='roadmap'||view==='roles'||view==='generate'||view==='summary'){
 const stage=view==='generate'?1:view==='summary'?phase([.25,.48,.7]):id==='u008'?0:id==='u009'?1:id==='u010'||id==='u011'?0:id==='u012'?(at(.52)?2:1):3;
 return <Workflow stage={stage} reached={view==='generate'||view==='summary'?3:id==='u010'||id==='u011'?1:stage} complete={id==='u102'}/>;
 }
 if(view==='automation'){const step=id==='u016'?phase([.29,.57]):0;return <><Head>Codex / Claude Code</Head>{id==='u014'||id==='u015'?<Big>会話で頼む。</Big>:<div style={{width:670}}>{[['Wan','API'],['Irodori','コード'],['Remotion','コマンド']].map(([a,b],i)=><div key={a} style={{opacity:i===step?1:i<step?.35:0,display:'flex',justifyContent:'space-between',padding:'18px 30px',fontSize:29,borderBottom:'1px solid #dce0d5'}}><span>{a}</span><span style={{color:green}}>← {b}</span></div>)}</div>}</>;}
 if(view==='environment')return <><Head>制作リポジトリ</Head><Row>{['手順','参照素材','実行コード'].map((x,i)=><Tile key={x} active={id==='u018'||phase([.13,.23])===i}>{x}</Tile>)}</Row><Small>最初の環境づくりは必要</Small></>;
 if(view==='human_review')return <Row>{['頼む','見る','直す'].map((x,i)=><React.Fragment key={x}>{i>0&&<Arrow/>}<Tile active={id==='u020'||phase([.38,.68])===i}>{x}</Tile></React.Fragment>)}</Row>;
 if(view==='request')return <><Head>替え玉出社</Head><Pair a="news_mask.jpg" b="news_sobaya.jpg" al="身代わりが出社" bl="本人は家で酒" focus={id==='u021'?(at(.48)?1:0):-1}/></>;
 if(view==='prompt_evidence'){
 const body=id==='u023'?at(.45):id==='u024'?phase([.28,.58])===1:false;
 return <><Pic name="news_mask.jpg" w={690} h={340}/><Row><Tile active={body}>体格：福ギュン</Tile><Tile active={!body}>仮面：そば屋</Tile></Row></>;
 }
 if(view==='prompt_model')return id==='u029'?<><Head>生成前に確認</Head><Row>{['人物','順番','オチ'].map((x,i)=><Tile key={x} active={phase([.53,.75])===i}>{x}</Tile>)}</Row></>:<><Head>指示を考えるモデルも大切</Head><Row><Tile>台本・意図</Tile><Arrow/><Tile active={false}>プロンプト</Tile><Arrow/><Tile active={id==='u028'}>生成映像</Tile></Row>{id==='u027'||id==='u028'?<div style={{color:purple,fontSize:31,marginTop:35}}>きれいでも、別のお話？</div>:null}</>;
 if(view==='sheet_identity')return <Pair a="news_fuku.jpg" b="park_fuku.jpg" al="ニュースの福ギュン" bl="CMの福ギュン"/>;
 if(view==='fuku_sheet')return <><Head>キャラクターシート</Head><Pic name="fuku_sheet.png" w={710} h={395}/></>;
 if(view==='faceless'||view==='ref_roles'){
 const face=view==='ref_roles'&&id==='u039'&&!at(.52);
 return <><Row><div style={{opacity:face?.3:1}}><Crop part="body"/><div style={{fontSize:25,marginTop:15,color:green}}>体格・服装</div></div><span style={{fontSize:32,color:'#9ba99c'}}>＋</span><div style={{opacity:view==='faceless'?.18:face||id==='u040'?1:.4}}><Crop part="face"/><div style={{fontSize:25,marginTop:15,color:purple}}>顔</div></div></Row></>;
 }
 if(view==='voice_sources')return <><Row><Tile active={id!=='u044'||!at(.25)}>声の見本<div style={{fontSize:45,letterSpacing:4,marginTop:15}}>▂▅▃▆▂</div></Tile><span style={{fontSize:32,opacity:id==='u044'?1:0}}>＋</span><Tile active={id==='u044'&&at(.25)} show={id==='u044'}>新しい台詞<div style={{fontSize:23,marginTop:22}}>「速報です…」</div></Tile></Row>{id==='u044'&&<div style={{opacity:reveal(.55),fontSize:32,color:green,marginTop:32}}>↓　Wan：映像 ＋ 声</div>}</>;
 if(['voice_problem','news_patch','sync'].includes(view))return <><Pic name="news_raw.jpg" h={370}/><div style={{fontSize:29,marginTop:20,color:purple}}>{view==='sync'?'声・長さ・口の動き':view==='news_patch'?'「速報です」を差し替え':'セリフだけ、惜しい。'}</div></>;
 if(view==='patch_cost')return <><Pic name="news_raw.jpg" w={590} h={275}/><div style={{display:'flex',gap:5,width:690,marginTop:25}}><div style={{width:150,padding:'18px 6px',background:'#ead5e3',color:purple,fontSize:25,borderBottom:`4px solid ${id==='u050'?purple:'transparent'}`}}>速報です</div><div style={{flex:1,padding:18,background:'#e2ebdf',fontSize:25}}>残りの音声は、そのまま</div></div>{id==='u050'&&<div style={{fontSize:25,color:purple,alignSelf:'flex-start',margin:'12px 0 0 45px'}}>↑ ここだけ交換</div>}</>;
 if(view==='park_intro'||view==='park_method')return <><Head>{view==='park_intro'?'元の尺に、入らない。':'一文から、切り出す。'}</Head><div style={{fontSize:29,lineHeight:2,padding:'22px 28px',background:'#e8ebe3',borderRadius:12}}>このTシャツ、<span style={{background:'#d8b9cf'}}>公式サイトでも</span><br/>買えるんですって。</div>{view==='park_method'&&<div style={{opacity:id==='u053'?1:reveal(.5),marginTop:25,fontSize:31,color:purple}}>↓<br/>公式サイトでも <span style={{fontSize:23}}>［1.2秒］</span></div>}<Small>第72話・別の修復実験</Small></>;
 if(view==='offscreen')return <Pair a="news_raw.jpg" b="news_sobaya.jpg" al="口元を見せる" bl="資料映像 ＋ 声" focus={1}/>;
 if(view==='news_before'||view==='news_after')return <><Pic name={view==='news_before'?'news_raw.jpg':'news.jpg'} w={710} h={420}/><Small>{view==='news_before'?'生成素材':'Remotionで字幕・テロップを追加'}</Small></>;
 if(view==='edit_demo'){const shifted=id!=='u060'||at(.24);return <><Head>「字幕を少し下へ」</Head><div style={{width:690,height:365,position:'relative',overflow:'hidden'}}><Pic name="news_raw.jpg" w={690} h={365}/><div style={{position:'absolute',left:25,right:25,bottom:shifted?18:75,background:'#253d44ee',padding:12,color:'white',fontSize:25}}>窓際社員「そば屋」に実刑判決</div></div><Small>説明用の再現</Small></>;}
 if(view==='repair')return <Row><Tile active={id==='u063'&&!at(.35)}>字幕・配置<br/><span style={{color:green}}>編集で直す</span></Tile><Tile active={id==='u064'||at(.35)}>顔・演技<br/><span style={{color:purple}}>生成を見直す</span></Tile></Row>;
 if(view==='price'){
 const stage=id==='u065'||id==='u066'?-1:id==='u067'?phase([.27,.47,.66])-1:3;
 return <><Head>30秒・1回の生成</Head><div style={{display:'flex',alignItems:'flex-end',gap:35,height:285,width:655}}>{[1.5,3,6].map((p,i)=><div key={p} style={{flex:1,opacity:stage<0?0:stage===3||i===stage?1:i<stage?.42:0}}><div style={{fontSize:35,fontWeight:700,marginBottom:12}}>${p.toFixed(2)}</div><div style={{height:p*27,background:i===2?purple:green,borderRadius:'6px 6px 0 0'}}/><div style={{fontSize:27,marginTop:12}}>{['480p','720p','1080p'][i]}</div></div>)}</div>{stage<0&&<div style={{position:'absolute',top:245,fontSize:39,color:green}}>秒数 × 解像度</div>}<Small>Qwen Cloud・通常表示価格｜2026-10-13確認｜動画生成分</Small></>;
 }
 if(view==='retry'){const stage=id==='u069'?phase([.25,.38]):2;return <><Head>作った分が、制作費。</Head><Row>{['候補1','候補2','採用'].map((x,i)=><Tile key={x} show={i<=stage} active={id==='u069'?i===stage:id==='u070'?true:i<2}>{x}<div style={{fontSize:32,marginTop:12}}>$1.50</div></Tile>)}</Row><div style={{opacity:id==='u069'?reveal(.6):1,fontSize:43,marginTop:38,color:purple}}>合計 $4.50</div><Small>480p・30秒 × 3回／通常表示価格</Small></>;}
 if(view==='resolution'||view==='highres')return <><Head>低解像度で試す</Head><Pic name="news_sobaya.jpg" w={510} h={250}/><div style={{marginTop:20,width:710}}><Row><Tile active={view==='resolution'&&id==='u072'}>そのまま採用</Tile><Tile show={id!=='u072'} active={id!=='u072'}>高解像度で再生成</Tile></Row></div>{id==='u077'&&<div style={{fontSize:27,color:purple,marginTop:22}}>演技・細部を、もう一度確認</div>}</>;
 if(view==='choice')return <><Head>窓際動画は、480pを採用</Head><Pair a="news_sobaya.jpg" b="park_sobaya.jpg" al="ニュース" bl="架空CM"/></>;
 if(view==='export')return <><Head>拡大と、再生成は別</Head><Row><Tile active={id==='u078'}>生成素材<br/><span style={{fontSize:42}}>480p</span></Tile><Arrow/><Tile active={id!=='u078'||at(.4)}>完成出力<br/><span style={{fontSize:42}}>720p</span></Tile></Row>{id!=='u078'&&<div style={{fontSize:29,marginTop:35,color:purple}}>字幕は鮮明に。元映像の細部は増えない。</div>}</>;
 if(view==='total')return <><Head>{id==='u081'?'生成料金のほかにも':'表示したのは、動画生成分。'}</Head>{id==='u081'?<Row>{['AIの利用料','実行環境','処理時間'].map((x,i)=><Tile key={x} active={phase([.32,.7])===i}>{x}</Tile>)}</Row>:<Big>実行時の価格を確認</Big>}</>;
 if(view==='logs')return <><Big>次の一本で、また詰まる？</Big><div style={{fontSize:75,color:purple,marginTop:30}}>↻</div></>;
 if(view==='skill_intro')return <><Big>スキル</Big><div style={{fontSize:28,color:grey,margin:'14px 0 35px'}}>AIが読む、制作手順書</div>{id!=='u084'&&<Row>{['手順','資料','コード'].map((x,i)=><Tile key={x} active={id==='u086'||phase([.45,.7])===i}>{x}</Tile>)}</Row>}</>;
 if(view==='api_failure'||view==='api_split'){
 const split=view==='api_split';const sum=split&&(id==='u089'||at(.5));
 return <><Head>{split?'短く分けても…':'声の見本が長すぎた'}</Head><div style={{width:690,display:'flex',gap:7,height:92}}>{(split?[8.53,8.46,13]:[30]).map((n,i)=><div key={i} style={{flex:n,background:sum?'#ead5e3':'#e2ebdf',display:'flex',alignItems:'center',justifyContent:'center',fontSize:29,borderRadius:8}}>{n}秒</div>)}</div><div style={{width:690,marginTop:14,borderTop:`3px solid ${sum?purple:'#a9b9a4'}`,paddingTop:15,fontSize:34,color:sum?purple:green}}>{split?(sum?'合計 約30秒 → ×':'1本ずつは15秒以内 → ✓'):'30秒 → ×'}</div><Small>当時の制限：1本・合計とも15秒まで（第53話の制作ログ）</Small></>;
 }
 if(view==='validation'){const step=id==='u090'?(at(.5)?1:0):2;return <><Head>送信する前に、確認</Head><Row><Tile active={step===0}>1本ずつの長さ</Tile><Tile active={step===1}>全部の合計</Tile></Row>{step===2&&<><div style={{fontSize:30,margin:'20px 0',color:grey}}>↓</div><Row><Tile active={false}>条件内 → 送信</Tile><Tile>条件外 → 停止</Tile></Row></>}</>;}
 if(view==='skill_reuse')return id==='u094'?<><Head>比較して、標準を更新</Head><Row><Tile active={false}>Small</Tile><Arrow/><Tile>Large</Tile></Row><Small>別の音声比較で、修正用に採用</Small></>:<><Head>採用した修復手順を残す</Head><Row><Tile>一文を生成</Tile><Arrow/><Tile>必要部分</Tile><Arrow/><Tile>スキルへ</Tile></Row></>;
 if(view==='skill_scope')return <><Head>{id==='u095'?'成功した設定を、全部に？':'使えた条件も、一緒に残す'}</Head><Row><Tile active={id==='u095'||id==='u096'||id==='u097'&&!at(.5)}>話者 A・短文</Tile><span style={{fontSize:40,color:purple}}>≠</span><Tile active={id==='u095'||id==='u097'&&at(.5)}>話者 B・長文</Tile></Row></>;
 if(view==='skill_loop')return <><Head>一本作るたび、作り方も育つ</Head><div style={{display:'grid',gridTemplateColumns:'1fr 40px 1fr',alignItems:'center',gap:18,width:690}}><Tile active={id==='u098'&&!at(.33)}>使ったもの</Tile><Arrow/><Tile active={id==='u098'&&at(.33)&&!at(.65)}>直したこと</Tile><div style={{fontSize:32,color:grey}}>↑</div><div/><div style={{fontSize:32,color:grey}}>↓</div><Tile active={id!=='u098'}>次の制作へ</Tile><span style={{fontSize:32,color:grey}}>←</span><Tile active={id==='u098'&&at(.65)}>確かめた範囲</Tile></div></>;
 if(view==='first_step')return <><Big>{id==='u105'?'できたら、一つ直す。':'一人、一場面。'}</Big><div style={{fontSize:31,color:grey,marginTop:30}}>{id==='u104'?'頭の中の一本を、外へ。':'短い動画から始めよう。'}</div></>;
 if(view==='h3')return <><Small>次回予告</Small><Head>h3さんの制作手法</Head>{id==='u106'?<div style={{fontSize:33,color:green}}>Seedance_Madogiwa</div>:<Row>{['料金','待ち時間','手作業'].map((x,i)=><Tile key={x} active={phase([.45,.8])===i}>{x}</Tile>)}</Row>}</>;
 if(view==='ending')return <Big>{id==='u108'?'財布と休日に、合う作り方。':'また、次の一本で。'}</Big>;
 throw Error('Unmapped view '+view);
};
