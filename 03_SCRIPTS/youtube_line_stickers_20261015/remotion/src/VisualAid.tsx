import React from 'react';
import {Img, staticFile} from 'remotion';
import rawStickers from '../public/stickers/manifest.json';
import {theme} from './theme';
import type {Dialogue} from './types';

const ids=['sobaya','takosan','tokun','yotan','fukuchan','yametaro','okayaman','yumemin'];
const names:Record<string,string>={sobaya:'そば屋',takosan:'たこさん',tokun:'とーくん',yotan:'よーたん',fukuchan:'福ギュン',yametaro:'やめ太郎',okayaman:'おかやまん',yumemin:'ゆめみん'};
const manifests=rawStickers as any;
const header:React.CSSProperties={fontSize:32,fontWeight:750,lineHeight:1.4,color:theme.blue,marginBottom:20};
const small:React.CSSProperties={fontSize:19,color:theme.muted,lineHeight:1.6};
const line:React.CSSProperties={border:`1px solid ${theme.border}`,padding:'16px 20px',fontSize:26,textAlign:'left',lineHeight:1.6};

function item(id:string):any {
 const all=manifests.members??manifests.stickers??manifests;
 return Array.isArray(all)?all.find((s:any)=>s.id===id):all[id];
}
export const Sticker:React.FC<{id:string;frame:number;width?:number;height?:number;still?:boolean;firstFrame?:boolean;style?:React.CSSProperties}>=({id,frame,width=200,height=170,still=false,firstFrame=false,style})=>{
 const s=item(id);const frames=s?.frames??[];
 const duration=s?.durationMs??s?.totalDurationMs??frames.reduce((sum:number,x:any)=>sum+(x.durationMs??100),0)??3000;
 const now=(frame*1000/30)%Math.max(1,duration);let elapsed=0;let chosen=frames[0];
 for(const x of frames){elapsed+=x.durationMs??100;if(now<elapsed){chosen=x;break;}}
 if(firstFrame)chosen=frames[0];
 const path=still?(s?.still??s?.stillPath??`stickers/${id}/stills/still.png`):(chosen?.path??chosen?.src??chosen?.file??`stickers/${id}/frames/000.png`);
 return <Img src={staticFile(path)} style={{width,height,objectFit:'contain',...style}}/>;
};
const Source:React.FC<{src:string;width?:number;height?:number}>=({src,width=700,height=370})=><Img src={staticFile(src)} style={{width,height,objectFit:'contain'}}/>;
const Pose:React.FC<{index:number;width?:number;height?:number}>=({index,width=260,height=170})=>{
 const scale=height/200;
 return <div style={{position:'relative',width,height,overflow:'hidden'}}><Img src={staticFile(manifests.sources.sobayaPoses[index])} style={{position:'absolute',width:320*scale,height:210*scale,left:(width-240*scale)/2-40*scale,top:-10*scale}}/></div>;
};
const Grid:React.FC<{frame:number;dark?:boolean}>=({frame,dark=false})=><div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'13px 12px',width:'100%',padding:10,boxSizing:'border-box',background:dark?'#101417':'#fff'}}>{ids.map(id=><div key={id}><Sticker id={id} frame={frame} width={166} height={145}/><div style={{fontSize:17,color:dark?'#fff':theme.muted}}>{names[id]}</div></div>)}</div>;
const Prompt:React.FC<{children:React.ReactNode;label?:string}>=({children,label='Codexへの指示例'})=><div style={{width:710,border:`2px solid ${theme.blue}`,textAlign:'left',boxSizing:'border-box'}}><div style={{fontSize:21,padding:'9px 18px',background:theme.yellow,color:theme.blue,fontWeight:700,borderBottom:`1px solid ${theme.border}`}}>{label}</div><div style={{fontSize:27,lineHeight:1.75,padding:'22px 25px',whiteSpace:'pre-line'}}>{children}</div></div>;
const Table:React.FC<{rows:string[][];active?:number}>=({rows,active=-1})=><div style={{width:710,borderTop:`1px solid ${theme.border}`,borderLeft:`1px solid ${theme.border}`}}>{rows.map((row,i)=><div key={i} style={{display:'flex',background:active===i?theme.yellow:i===0?'#eff3f0':'#fff'}}>{row.map((text,j)=><div key={j} style={{...line,width:j===0?'35%':'65%',boxSizing:'border-box',borderTop:0,borderLeft:0,fontWeight:i===0?700:500,color:active===i?theme.blue:theme.ink,whiteSpace:'pre-line'}}>{text}</div>)}</div>)}</div>;

const Chat:React.FC<{frame:number;withMessage?:boolean}>=({frame,withMessage=true})=><div style={{width:710,height:448,border:'1px solid #b1becb',overflow:'hidden',textAlign:'left',background:'#d9e8f6'}}>
 <div style={{height:50,background:'#fff',display:'flex',alignItems:'center',padding:'0 20px',gap:18,fontSize:24,fontWeight:700}}><span style={{fontSize:32}}>‹</span><span>よーたん</span><span style={{marginLeft:'auto',fontWeight:400,fontSize:20}}>☎　≡</span></div>
 <div style={{padding:'12px 24px',display:'flex',gap:16}}><div style={{width:44,height:44,borderRadius:50,background:'#fff',fontSize:24,display:'flex',alignItems:'center',justifyContent:'center'}}>よ</div><div><div style={{fontSize:16,marginBottom:5,color:'#4a6072'}}>よーたん</div><Sticker id="yotan" frame={frame} width={285} height={240}/></div></div>
 {withMessage&&<div style={{display:'inline-block',marginLeft:84,padding:'13px 21px',background:'#fff',borderRadius:14,fontSize:24,lineHeight:1.55,position:'relative',top:-15}}>栄転おめでとう！<br/>詳しくは辞令のメール見てね😊</div>}
</div>;
const Outlook:React.FC<{focus?:boolean}>=({focus=false})=><div style={{width:740,height:455,background:'#fff',border:'1px solid #bac8d8',textAlign:'left',color:'#242424',boxShadow:'0 4px 12px #0000000d'}}>
 <div style={{height:46,background:'#0f6cbd',color:'white',display:'flex',alignItems:'center',padding:'0 17px',gap:17,fontSize:23,fontWeight:600}}><div style={{background:'#fff',color:'#0f6cbd',fontSize:22,width:29,height:29,textAlign:'center'}}>O</div>Outlook<div style={{height:24,width:240,marginLeft:40,background:'#e5f1fb',borderRadius:3,color:'#58718b',fontSize:15,padding:'2px 12px'}}>⌕　検索</div></div>
 <div style={{height:33,borderBottom:'1px solid #d7dfe8',display:'flex',alignItems:'center',gap:26,paddingLeft:18,fontSize:15,background:'#fafbfc'}}>新しいメール　　削除　　アーカイブ　　返信</div>
 <div style={{display:'flex',height:374}}><div style={{width:140,flexShrink:0,padding:'21px 13px',boxSizing:'border-box',background:'#f4f5f7',borderRight:'1px solid #dce1e7',fontSize:17,lineHeight:2.35}}><div style={{fontWeight:700,color:'#0f6cbd',whiteSpace:'nowrap',fontSize:16}}>受信トレイ <span style={{marginLeft:4}}>1</span></div>下書き<br/>送信済み<br/>アーカイブ</div>
  <div style={{flex:1,padding:'18px 24px'}}><div style={{fontSize:24,fontWeight:700,marginBottom:11}}>【辞令】異動のお知らせ</div><div style={{fontSize:17,paddingBottom:12,borderBottom:'1px solid #dbe1e6',marginBottom:16}}><b>よーたん</b><br/><span style={{color:'#666'}}>宛先：やめ太郎</span></div><div style={{fontSize:22,lineHeight:1.8}}>やめ太郎 殿<br/>明日付で、ゆめみ村への赴任を命じます。<br/>本異動は栄転となります。<br/><div style={{display:'inline-block',fontSize:24,fontWeight:700,marginTop:16,padding:'4px 10px',marginLeft:-10,background:focus?'#fff1c3':'transparent',borderBottom:focus?'3px solid #d58a16':'3px solid transparent'}}>赴任先：ゆめみ村（廃村）</div></div></div>
 </div>
</div>;

export const VisualAid:React.FC<{view:string;frame:number;utterance?:Dialogue;chatStart?:number}>=({view,frame,utterance,chatStart=0})=>{
 const text=utterance?.text??'';const focus=utterance?.focus;
 const local=frame-(utterance?.startFrame??0);
 const progress=local/Math.max(1,utterance?.durationInFrames??1);
 const cueStart=(phrase:string)=>{
  const segment=utterance?.captionSegments?.find(x=>x.text.replace(/\n/g,'').includes(phrase));
  if(segment){const words=segment.text.replace(/\n/g,'');return segment.startFrame+(segment.endFrame-segment.startFrame)*words.indexOf(phrase)/Math.max(1,words.length);}
  return Math.max(0,text.indexOf(phrase))/Math.max(1,text.length)*(utterance?.durationInFrames??1);
 };
 const aliases:Record<string,string>={readability:'small-preview','fixed-caption':'fixed-text',methods:'other-methods','caption-alpha':'alpha-text',checks:'spec-check'};view=aliases[view]??view;
 if(view==='line-chat'||view==='opening-chat'||view==='chat')return <Chat frame={Math.max(0,frame-chatStart)} withMessage={frame>=chatStart+27}/>;
 if(view==='store')return <><div style={header}>LINE STOREで販売中</div><div style={{display:'flex',width:700,border:'1px solid #c8d1cc',padding:25,gap:30,alignItems:'center',boxSizing:'border-box'}}><Source src={manifests.store.mainImage} width={240} height={240}/><div style={{textAlign:'left',flex:1}}><div style={{fontSize:19,color:'#06a847',fontWeight:700,marginBottom:17}}>LINE STORE 掲載情報</div><div style={{fontSize:33,fontWeight:750,lineHeight:1.55}}>窓際族スタンプ<br/>第一弾</div><div style={{fontSize:23,marginTop:18,lineHeight:1.7}}>アニメーションスタンプ<br/>申請担当：そば屋さん</div></div></div><div style={{...small,marginTop:20}}>販売ページは概要欄へ</div></>;
 if(view==='outlook'||view.startsWith('outlook-'))return <Outlook focus={/ガチ|ハイソン|廃村|Python/.test(text)||view==='outlook-focus'}/>;
 if(view==='greeting')return <><div style={{...header,fontSize:40}}>やめ太郎 ＆ たこさん</div><div style={{fontSize:25,marginBottom:35}}>Codexで動くLINEスタンプを作る</div><div style={{display:'flex',gap:35}}><Sticker id="yametaro" frame={frame} width={230} height={210}/><Sticker id="takosan" frame={frame} width={230} height={210}/></div></>;
 if(view==='opening-grid'||view==='ending'||view==='showcase'||view==='grid')return <><div style={header}>窓際族LINEスタンプ第一弾</div><Grid frame={frame}/>{view==='ending'&&<div style={{...small,marginTop:12}}>販売ページ・制作資料は概要欄へ</div>}</>;
 if(view==='overview'||view==='workflow'){
  const stages=[['① ネタ','セリフ・使う場面'],['② 静止画','キャラ・構図を決める'],['③ 連続原画','動きの途中を描く'],['④ 組み立て','切り出し・順番・間'],['⑤ 仕上げ','透過・APNG・確認']];
  const active=utterance?.id==='flow-03'?['ネタ','静止画','動きの原画','切り出し','最後に'].reduce((last,phrase,i)=>local>=cueStart(phrase)?i:last,0):typeof focus==='number'?focus:/ネタ|セリフ/.test(text)?0:/静止|顔|構図/.test(text)?1:/原画/.test(text)?2:/コード|切|つな|組/.test(text)?3:/透過|ファイル|規格/.test(text)?4:-1;
  return <><div style={header}>制作の流れ</div><Table rows={stages} active={active}/></>;
 }
 if(view==='roles'){
  const talkingPlan=utterance?.id==='flow-05'&&local>=cueStart('ChatGPT');
  const talkingHuman=utterance?.id==='flow-07'&&local>=cueStart('人は');
  const talkingCode=utterance?.id==='flow-07'&&!talkingHuman;
  const talkingImage=utterance?.id==='flow-05'&&!talkingPlan;
  const box=(active:boolean):React.CSSProperties=>({border:`3px solid ${active?theme.blue:'#d8e0db'}`,background:active?theme.yellow:'#fff',boxSizing:'border-box'});
  return <><div style={header}>原画づくりから、Codexで進める</div>
   <div style={{display:'flex',alignItems:'center',width:720,gap:14}}>
    <div style={{...box(talkingHuman),width:195,padding:'25px 10px',fontSize:23,lineHeight:1.8,flexShrink:0}}><div style={{fontSize:30,fontWeight:750,marginBottom:10}}>人</div>ネタ・使う場面<br/>仕上がりの判断</div>
    <div style={{fontSize:37,color:theme.blue}}>→</div>
    <div style={{border:`3px solid ${theme.blue}`,flex:1,textAlign:'left',background:'#fff'}}>
     <div style={{padding:'9px 18px',background:theme.blue,color:'white',fontSize:30,fontWeight:750}}>Codex</div>
     <div style={{padding:13,display:'flex',flexDirection:'column',gap:10}}>
      <div style={{...box(talkingImage),padding:'12px 17px'}}><div style={{fontSize:27,fontWeight:750,color:theme.blue}}>Imagegen</div><div style={{fontSize:24,marginTop:5}}>OpenAIのモデルで原画生成</div></div>
      <div style={{...box(talkingCode),padding:'12px 17px'}}><div style={{fontSize:27,fontWeight:750,color:theme.blue}}>コード</div><div style={{fontSize:24,marginTop:5}}>加工・書き出し・検証</div></div>
     </div>
    </div>
   </div>
   <div style={{fontSize:21,lineHeight:1.6,marginTop:20,padding:'5px 10px',background:talkingPlan?theme.yellow:'transparent',color:talkingPlan?theme.blue:theme.muted,fontWeight:talkingPlan?700:500}}>ChatGPT対応プランに含まれるCodexの利用枠を使用</div>
  </>;
 }
 if(view==='reference'||view==='reference-sheet')return <><div style={header}>人物の特徴と、絵柄をそろえる</div><div style={{display:'flex',alignItems:'center',gap:20}}><Source src={manifests.sources.sobayaCanonicalSheet} width={425} height={310}/><div style={{fontSize:32,color:theme.blue}}>→</div><Sticker id="sobaya" frame={frame} still width={225} height={250}/></div><div style={small}>参照画像の役割を伝える：人物同一性 ／ イラストのタッチ</div></>;
 if(view==='sobaya-still'&&utterance?.id?.startsWith('main-'))view='sobaya';
 if(view==='sobaya-still'||view==='sobaya')return <><div style={header}>止まった絵でも、気持ちが伝わる</div><Sticker id="sobaya" frame={frame} still={view==='sobaya-still'} width={400} height={338}/></>;
 if(view==='small-preview')return <><div style={header}>スタンプの大きさで読める？</div><div style={{display:'flex',alignItems:'center',gap:55}}><Sticker id={utterance?.id==='still-09'?'yametaro':'sobaya'} frame={frame} still width={320} height={270}/><div style={{fontSize:36}}>→</div><div style={{padding:20,background:'#dce9f5'}}><Sticker id={utterance?.id==='still-09'?'yametaro':'sobaya'} frame={frame} still width={160} height={135}/></div></div></>;
 if(view==='yotan-sheet'||view==='sheet'){
  const cutting=utterance?.id==='sheet-04';const cutStart=cueStart('あとで');const cell=Math.min(5,Math.max(0,Math.floor((local-cutStart)/Math.max(1,(utterance?.durationInFrames??1)-cutStart)*6)));
  return <><div style={header}>一枚に、動きの続きを描く</div><div style={{position:'relative',width:665,height:360}}><Source src={manifests.sources.yotanSheet} width={665} height={360}/>{cutting&&local>=cutStart&&<div style={{position:'absolute',left:62.5+(cell%3)*180,top:Math.floor(cell/3)*180,width:180,height:180,boxSizing:'border-box',border:`4px solid ${theme.blue}`,background:'#176B4709'}}><div style={{position:'absolute',top:0,left:0,padding:'3px 9px',background:theme.blue,color:'white',fontSize:19}}>{cell+1} コマ目</div></div>}</div><div style={small}>実際に使用した連続原画 ／ 3列 × 2行</div></>;
 }
 if(view==='prompt'||view==='sheet-prompt')return <><div style={header}>始まり・終わり・保つ部分を伝える</div><Prompt>指差しするまでの連続した6つの姿勢を、{`\n`}3列×2行に描いて。{`\n`}顔・服・カメラ位置・大きさをそろえて。{`\n`}各コマに余白を取り、文字は描かないで。</Prompt></>;
 if(view==='sobaya-poses'||view==='poses')return <><div style={{...header,marginBottom:12}}>採用した、そば屋の原画4枚</div><div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:'6px 48px'}}>{[0,1,2,3].map(i=><div key={i} style={{display:'flex',alignItems:'center'}}><div style={{...small,color:theme.blue,fontWeight:700,writingMode:'vertical-rl'}}>原画 {i+1}</div><Pose index={i}/></div>)}</div><div style={{...small,marginTop:10}}>顔とジョッキを保ち、手と腕で動きを作る</div></>;
 if(view==='sequence'||view==='timing'||view==='fixed-text'){
  const order=[0,1,2,3,2,1,0,1,2,3,2,1];const elapsed=(frame*1000/30)%3000;const selected=elapsed<1080?order[Math.floor(elapsed/90)]:0;
  return <><div style={header}>{view==='fixed-text'?'文字は、一枚を同じ位置に重ねる':'往復と「間」で、演技にする'}</div><div style={{display:'flex',gap:25,alignItems:'center'}}><div><Sticker id="sobaya" frame={frame} width={300} height={270}/><div style={{...small,marginTop:5}}>二回なでる → 余韻</div></div><div style={{width:370}}><div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:4}}>{[0,1,2,3].map(i=><div key={i} style={{border:`2px solid ${selected===i?theme.blue:'#d4ded8'}`,background:selected===i?theme.yellow:'#fff'}}><Source src={manifests.sources.sobayaPoses[i]} width={85} height={125}/></div>)}</div><div style={{fontSize:26,marginTop:22,lineHeight:1.8}}>原画 <b>4枚</b><br/>往復 ＋ 最後に止める<br/>完成 <b>13フレーム・3秒</b></div></div></div></>;
 }
 if(view==='alignment')return <><div style={header}>動かさない部分を、そろえる</div><div style={{display:'flex',gap:24,alignItems:'center'}}><div style={{position:'relative',width:340,height:295,border:'1px solid #c8d1cc'}}><Sticker id="sobaya" frame={frame} width={340} height={295}/><div style={{position:'absolute',left:38,right:38,bottom:31,borderTop:'2px dashed #176B47'}}/></div><div style={{textAlign:'left',fontSize:28,lineHeight:1.85}}>全コマで位置と大きさを統一<br/><span style={{color:theme.blue}}>顔・ジョッキを基準にする</span><br/>手と腕で、動きを見せる</div></div><div style={{...small,marginTop:25}}>同じ切り出し範囲・同じ倍率で配置</div></>;
 if(view==='other-methods')return <><div style={header}>絵に合う動かし方を選ぶ</div><div style={{display:'flex',gap:25}}>{['takosan','okayaman','yumemin'].map(id=><div key={id}><Sticker id={id} frame={frame} width={215} height={215}/><div style={small}>{names[id]}</div></div>)}</div><div style={{...small,marginTop:24}}>第一弾では、補間や絵全体の拡大・回転も使用</div></>;
 if(view==='alpha-text')return <><div style={header}>文字の穴と、細い白フチまで確認</div><div style={{display:'flex',gap:20}}>{[false,true].map(dark=><div key={String(dark)}><div style={{...small,marginBottom:6}}>{dark?'黒背景':'白背景'}</div><div style={{position:'relative',width:340,height:100,overflow:'hidden',background:dark?'#0b0d10':'white',border:'1px solid #bdc9c1'}}><Img src={staticFile(item('sobaya').frames[0].path)} style={{position:'absolute',width:448,height:378,left:-60,top:5}}/></div></div>)}</div><div style={{display:'flex',alignItems:'center',gap:32,marginTop:20}}><Sticker id="sobaya" frame={frame} firstFrame width={210} height={177}/><div style={{fontSize:26,lineHeight:1.85,textAlign:'left'}}>文字の内側は背景が見える<br/><span style={{color:theme.blue}}>白フチは、読めるための線</span><br/><span style={small}>完成APNGの先頭フレームを拡大</span></div></div></>;
 if(view==='alpha'||view==='alpha-white'||view==='alpha-black'||view==='alpha-protect'||view==='alpha-text'){
  const dark=view==='alpha-black'||view==='alpha-text';const protect=view==='alpha-protect'||/服|顔|泡|白いところ/.test(text);const letters=view==='alpha-text'||/文字|穴|内側/.test(text);
  return <><div style={header}>{protect?'背景の白と、絵の中の白を分ける':letters?'文字の内側と、輪郭まで確認':'白背景と黒背景で見比べる'}</div><div style={{display:'flex',gap:18,alignItems:'center'}}><div style={{background:dark?'#0b0d10':'#fff',border:'1px solid #c8d1cc',width:355,height:315,display:'flex',justifyContent:'center',alignItems:'center'}}><Sticker id="sobaya" frame={frame} width={330} height={280}/></div><div style={{width:310,textAlign:'left',fontSize:27,lineHeight:1.85}}>{protect?<><div style={{color:theme.alert}}>消す：背景</div><div style={{color:theme.blue}}>残す：白Tシャツ<br/>　　　顔・ビールの泡</div></>:letters?<>文字の穴を透過<br/>輪郭の白残りを確認<br/><span style={{color:theme.blue}}>細い白フチは残す</span></>:<>白では目立たない<br/>輪郭の残りも、<br/>黒で確認できる</>}</div></div><div style={{...small,marginTop:17}}>完成ファイルを再生して、途中のコマも確認</div></>;
 }
 if(view==='compare-grid')return <><div style={header}>8個を、白と黒の背景で確認</div><div style={{display:'flex',gap:12,width:740}}>{[false,true].map(dark=><div key={String(dark)} style={{width:364,height:330,overflow:'hidden',background:dark?'#101417':'white',border:'1px solid #c8d1cc'}}><div style={{fontSize:18,padding:9,color:dark?'white':theme.ink}}>{dark?'黒背景':'白背景'}</div><div style={{width:740,transform:'scale(.49)',transformOrigin:'top left'}}><Grid frame={frame} dark={dark}/></div></div>)}</div></>;
 if(view==='files'||view==='gif-apng')return <><div style={header}>確認用と、申請用を分ける</div><Table rows={[["用途","形式"],["確認用","GIF ／ 白・黒背景"],["申請用","APNG ／ 透明な背景"],["拡張子","動いても .png"]]} active={/GIF/.test(text)?1:2}/></>;
 if(view==='specs'||view==='main-tab')return <><div style={header}>LINEへ提出する画像</div><Table rows={[["画像","形式・サイズ"],["スタンプ × 8","APNG ／ 最大320×270px"],["メイン × 1","APNG ／ 240×240px"],["タブ × 1","静止PNG ／ 96×74px"]]} active={/メイン|タブ/.test(text)?2:1}/><div style={{...small,marginTop:13}}>本体：縦横いずれか270px以上 ／ 各画像1MB以下</div></>;
 if(view==='first-frame')return <><div style={header}>最初の一コマでも、意味が伝わる</div><div style={{display:'flex',gap:28}}><div style={{border:'1px solid #c8d1cc',padding:15}}><div style={{fontSize:23,color:theme.blue,marginBottom:10}}>先頭フレーム</div><Sticker id="yametaro" frame={frame} firstFrame width={290} height={245}/></div><div style={{border:'1px solid #c8d1cc',padding:15}}><div style={{fontSize:23,color:theme.blue,marginBottom:10}}>アニメーション</div><Sticker id="yametaro" frame={frame} width={290} height={245}/></div></div><div style={{...small,marginTop:20}}>どちらも、完成APNGから表示</div></>;
 if(view==='spec-check'||view==='first-frame')return <><div style={header}>{view==='first-frame'?'最初の一コマでも意味が伝わる':'規格と、見た目の両方を確認'}</div><div style={{display:'flex',alignItems:'center',gap:25}}><Sticker id="yametaro" frame={frame} firstFrame={view==='first-frame'} width={300} height={270}/><div style={{fontSize:27,lineHeight:1.9,textAlign:'left'}}>5〜20フレーム<br/>再生時間は合計4秒以内<br/>最初のコマも確認<br/>書き出したAPNGを再生</div></div></>;
 if(view==='records')return <><div style={header}>完成品と、一緒に残すもの</div><Table rows={[["採用した絵","参照画像・原画"],["生成の指示","どんな動きを頼んだか"],["加工コード","切り出し・透過・書き出し"],["制作記録","順番・間・直したところ"]]}/></>;
 if(view==='skill')return <><div style={header}>次にも使う手順を、スキルにする</div><div style={{width:700,textAlign:'left',border:`2px solid ${theme.blue}`}}><div style={{padding:'10px 22px',fontSize:22,background:theme.yellow,color:theme.blue,fontWeight:700}}>line-stickers / SKILL.md</div><div style={{padding:'22px 28px',fontSize:28,lineHeight:1.9}}>採用原画と、実際の組立コードを読む<br/>連続した原画から動きを作る<br/>白背景・黒背景で透過を確認する<br/>main・tabと規格チェックまで行う</div></div></>;
 if(view==='start-prompt')return <><div style={header}>まずは、一個から</div><Prompt>このキャラクターで、動くLINEスタンプを作りたい。{`\n`}まずセリフと動きの案を考えて、{`\n`}静止画で方向性を決めたい。{`\n`}連続原画から動かして、白と黒で確認したい。</Prompt></>;
 if(view==='yametaro'||view==='end-joke')return <><div style={header}>ごめんやで</div><Sticker id="yametaro" frame={frame} width={420} height={355}/></>;
 return <><div style={header}>窓際族スタンプ第一弾</div><Grid frame={frame}/></>;
};
