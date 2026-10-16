import React from 'react';
import {Img, staticFile} from 'remotion';
import assets from './tips-assets.json';
import firstSet from '../public/stickers/manifest.json';
import prompts from '../tip-prompts.json';
import {Sticker} from './VisualAid';
import {theme} from './theme';
import type {Dialogue} from './types';

// The source images and motion candidates are actual production materials.
// Crops / animation frames are prepared without drawing new visual evidence.
const a=assets as any;
const first=firstSet as any;
const memberIds=['sobaya','takosan','tokun','yotan','fukuchan','yametaro','okayaman','yumemin'];
const H:React.FC<{children:React.ReactNode}>=({children})=><div style={{fontSize:32,fontWeight:750,lineHeight:1.4,color:theme.blue,marginBottom:16}}>{children}</div>;
const Note:React.FC<{children:React.ReactNode}>=({children})=><div style={{fontSize:19,lineHeight:1.55,color:theme.muted,marginTop:12}}>{children}</div>;
const Image:React.FC<{name:string;width?:number;height?:number;style?:React.CSSProperties}>=({name,width=320,height=280,style})=><Img src={staticFile(a.images[name].path)} style={{width,height,objectFit:'contain',...style}}/>;
const Animation:React.FC<{name:string;frame:number;width?:number;height?:number;style?:React.CSSProperties}>=({name,frame,width=320,height=280,style})=>{
 const s=a.animations[name];const now=(frame*1000/30)%s.durationMs;
 const chosen=s.frames.find((x:any)=>now>=x.startMs&&now<x.endMs)??s.frames[0];
 return <Img src={staticFile(chosen.path)} style={{width,height,objectFit:'contain',...style}}/>;
};
const Label:React.FC<{children:React.ReactNode;active?:boolean}>=({children,active=false})=><div style={{fontSize:23,fontWeight:700,padding:'8px 13px',color:active?'#fff':theme.blue,background:active?theme.blue:'#eff4f0',lineHeight:1.45}}>{children}</div>;
const FirstGrid:React.FC<{frame:number;dark?:boolean}>=({frame,dark=false})=><div style={{width:715,background:dark?'#101417':'#fff',display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'12px 10px',padding:12,boxSizing:'border-box',border:`1px solid ${theme.border}`}}>{memberIds.map(id=><Sticker key={id} id={id} frame={frame} width={163} height={140}/>)}</div>;
const SecondGrid:React.FC<{frame:number}>=({frame})=><div style={{width:715,background:'#fff',display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'12px 10px',padding:12,boxSizing:'border-box',border:`1px solid ${theme.border}`}}>{a.secondSet.map((name:string)=><Animation key={name} name={name} frame={frame} width={163} height={140}/>)}</div>;
const Prompt:React.FC<{lines:string[];active:number}>=({lines,active})=><div style={{width:715,textAlign:'left',border:`2px solid ${theme.blue}`,boxSizing:'border-box'}}><div style={{fontSize:22,fontWeight:700,padding:'10px 21px',background:theme.blue,color:'white'}}>Codexへの指示例</div><div style={{padding:'16px 17px',fontSize:28,lineHeight:1.7}}>{lines.map((line,i)=><div key={i} style={{padding:'4px 10px',background:active===i?theme.yellow:'white',borderLeft:`4px solid ${active===i?theme.blue:'transparent'}`}}>{line}</div>)}</div></div>;

export const tipsViews=new Set(['tip-intro','plan-teaser','second-grid','idea-grid','idea-speed','idea-prompt','codex-settings','option-compare','option-reuse','redraw-compare','redraw-prompt','pets-sheet','pets-process','pets-prompt','acting-sobaya','acting-work','acting-prompt','acting-options','inspect-history-white','inspect-history-black','inspect-history-report','inspect-whiteblack','inspect-details','inspect-prompt','tools-beforeafter','tools-choice','tools-prompt','closing-flow','ending']);

export const TipsVisualAid:React.FC<{view:string;frame:number;utterance:Dialogue;viewStart?:number}>=({view,frame,utterance:d,viewStart})=>{
 const local=frame-d.startFrame;const progress=local/Math.max(1,d.durationInFrames);const text=d.text;
 // Visual media uses continuous chapter/view time. Caption changes never reset a GIF.
 const mediaFrame=frame-(viewStart??d.startFrame);
 const cue=(phrase:string)=>{
  const segment=d.captionSegments?.find(x=>x.text.replace(/\n/g,'').includes(phrase));
  if(segment){const words=segment.text.replace(/\n/g,'');return segment.startFrame+(segment.endFrame-segment.startFrame)*words.indexOf(phrase)/Math.max(1,words.length);}
  const i=text.indexOf(phrase);return i<0?Infinity:i/Math.max(1,text.length)*d.durationInFrames;
 };
 const after=(phrase:string)=>local>=cue(phrase);
 const prompt=(heading:string,lines:string[],phrases:string[]=[])=>{
  const canonical=(prompts as Record<string,string>)[view];
  if(canonical.replace(/\n/g,'')!==lines.join(''))throw new Error(`Prompt text differs from tip-prompts.json: ${view}`);
  const matching=phrases.some(p=>text.includes(p));
  let active=matching?phrases.reduce((last,p,i)=>after(p)?i:last,0):Math.min(lines.length-1,Math.floor(Math.max(0,progress)*lines.length));
  if(view==='pets-prompt')active=after('頼むとき')?0:1;
  if(view==='acting-prompt')active=after('そのうえで')?0:-1;
  return <><H>{heading}</H><Prompt lines={lines} active={active}/><Note>自分のキャラクターや、作りたいネタに置き換えて使えます</Note></>;
 };
 if(view==='tip-intro'){
  if(d.id==='tips-05')return <><H>絵づくりも、同じチャットから</H><div style={{width:690,border:`3px solid ${theme.blue}`,textAlign:'left'}}><div style={{padding:'12px 23px',fontSize:31,fontWeight:750,background:theme.blue,color:'white'}}>Codex</div><div style={{padding:25,background:after('対応する')?'white':theme.yellow}}><div style={{fontSize:34,fontWeight:750,color:theme.blue}}>Imagegen</div><div style={{fontSize:27,marginTop:12}}>OpenAIの画像生成モデルで絵を作る</div></div><div style={{fontSize:25,lineHeight:1.65,padding:'18px 25px',borderTop:`1px solid ${theme.border}`,background:after('対応する')?theme.yellow:'white'}}>対応するChatGPTプランに含まれる<br/><b>Codexの利用枠</b>で使える</div></div></>;
  if(d.id==='tips-03')return <><H>作って分かった、頼み方・選び方・直し方</H><div style={{display:'flex',gap:15,width:715}}>{[['頼み方','まず、まとめて見る'],['選び方','候補を見比べる'],['直し方','絵を保って整える']].map(([label,detail],i)=><div key={label} style={{flex:1,border:`3px solid ${i===(after('気に入らない')?1:0)?theme.blue:theme.border}`,background:i===(after('気に入らない')?1:0)?theme.yellow:'white',padding:'25px 8px'}}><div style={{fontSize:30,fontWeight:700,color:theme.blue,marginBottom:20}}>{label}</div><div style={{fontSize:22}}>{detail}</div></div>)}</div><div style={{display:'flex',gap:20,marginTop:20}}><Sticker id="sobaya" frame={mediaFrame} width={220} height={190}/><Sticker id="yotan" frame={mediaFrame} width={220} height={190}/></div></>;
  return <><H>第一弾と第二弾を作って分かったこと</H><FirstGrid frame={mediaFrame}/><Note>第一弾は8人。続く第二弾の制作例も使って解説します</Note></>;
 }
 if(view==='second-grid')return <><H>第二弾は、そば屋だけで8個</H><SecondGrid frame={mediaFrame}/><Note>案出し・候補選び・動き作りは、この第二弾の実例で</Note></>;
 if(view==='plan-teaser')return <><H>ChatGPTのプラン、どう選ぶ？</H><div style={{width:690,border:`3px solid ${theme.blue}`,padding:'34px 30px',boxSizing:'border-box',textAlign:'left'}}><div style={{fontSize:24,color:theme.muted,marginBottom:20}}>今後取り上げたいテーマ</div><div style={{fontSize:35,fontWeight:750,color:theme.blue,lineHeight:1.6}}>コンテンツ制作を目的にした<br/>ChatGPTプランの選び方</div><div style={{borderTop:`1px solid ${theme.border}`,marginTop:25,paddingTop:20,fontSize:24}}>どのくらい作るか、何に使うか</div></div><Note>今回は、LINEスタンプの作り方を紹介します</Note></>;
 if(view==='idea-speed'){
  const stage=d.id==='ideas-speed-02'?0:d.id==='ideas-speed-03'?(after('仕上げ')?1:0):-1;
  return <><H>まとめて生成すると、検討が速くなる</H><div style={{width:710,display:'flex',gap:20,alignItems:'center'}}><div style={{width:292,border:`2px solid ${theme.blue}`}}><Image name="ideasA" width={288} height={188}/><Label>1枚で8個を比較</Label></div><div style={{fontSize:33,color:theme.blue}}>→</div><div style={{flex:1,fontSize:28,lineHeight:1.65,textAlign:'left',color:theme.blue,fontWeight:700}}>Imagegenの<br/>呼び出し回数を減らす<br/><span style={{fontSize:22,color:theme.muted,fontWeight:500}}>案を見て、すぐ次を試す</span></div></div><div style={{width:710,display:'flex',gap:16,marginTop:22}}>{[['案出し','人が見比べながら進める','速度を優先'],['仕上げ','任せて、完成を待つ','クオリティを優先']].map(([label,detail,priority],i)=><div key={label} style={{flex:1,textAlign:'left',border:`3px solid ${stage===i?theme.blue:theme.border}`,background:stage===i?theme.yellow:'white',padding:'13px 18px'}}><div style={{fontSize:25,fontWeight:750,color:theme.blue}}>{label}：{priority}</div><div style={{fontSize:20,marginTop:9}}>{detail}</div></div>)}</div></>;
 }
 if(view==='codex-settings'){
  const selected=d.id==='settings-02'?0:d.id==='settings-03'?1:-1;
  return <><H>投稿者は、フェーズでCodexの設定を変える</H><div style={{width:710,border:`2px solid ${theme.blue}`,boxSizing:'border-box'}}><div style={{display:'flex',alignItems:'center',padding:'14px 21px',background:theme.blue,color:'#fff',textAlign:'left'}}><span style={{fontSize:23}}>モデル</span><b style={{fontSize:31,marginLeft:30}}>GPT 6 Astra</b></div><div style={{display:'flex'}}>{[['案出し','Light','やり取りの速さを優先'],['仕上げ','Ultra','時間をかけて仕上げる']].map(([phase,effort,detail],i)=><div key={phase} style={{flex:1,padding:'24px 10px',background:selected===i?theme.yellow:'white',borderRight:i===0?`1px solid ${theme.border}`:undefined}}><div style={{fontSize:27,fontWeight:750,color:theme.blue}}>{phase}</div><div style={{fontSize:24,marginTop:17,color:theme.muted}}>effort <b style={{fontSize:39,color:theme.blue,marginLeft:8}}>{effort}</b></div><div style={{fontSize:21,marginTop:18}}>{detail}</div></div>)}</div></div><div style={{fontSize:25,fontWeight:700,color:theme.blue,marginTop:21}}>好みや、待てる時間に合わせて変えてOK</div><Note>Codexの推論設定です。Imagegenの画質設定とは別です</Note></>;
 }
 if(view==='idea-grid'){
  const selected=d.id==='ideas-07'?Math.min(2,Math.floor(progress*3)):d.id==='ideas-08'?2:0;
  const key=['ideasA','ideasB','ideasC'][selected];
  return <><H>最初は、1枚に8個まとめて出す</H><div style={{display:'flex',gap:16,alignItems:'center',width:725}}><div style={{width:572,height:346,border:`2px solid ${theme.blue}`,position:'relative',background:'#fff'}}><Image name={key} width={568} height={342}/><div style={{position:'absolute',right:5,bottom:5,padding:'5px 12px',fontSize:20,fontWeight:700,background:theme.blue,color:'white'}}>案 {['A','B','C'][selected]}</div></div><div style={{display:'flex',flexDirection:'column',gap:10}}>{['ideasA','ideasB','ideasC'].map((name,i)=><div key={name} style={{width:128,border:`3px solid ${selected===i?theme.blue:'#d1dbd4'}`,background:selected===i?theme.yellow:'white',padding:3}}><div style={{fontSize:18,fontWeight:700,color:theme.blue}}>案 {['A','B','C'][i]}</div><Image name={name} width={122} height={72}/></div>)}</div></div><Note>{d.id==='ideas-05'||d.id==='ideas-06'?'セットで見ると、ポーズや構図の偏りが分かる':d.id==='ideas-09'?'細かな仕上げの前に、作りたい方向を選ぶ':'第二弾の案出しで実際に生成した3パターン'}</Note></>;
 }
 if(view==='idea-prompt')return prompt('一覧で見て、方向を選ぶ',['まずは案出し用に、1枚の画像に','8種類のスタンプを並べて。','ポーズや構図が似すぎないように、','何パターンか見せて。']);
 if(view==='option-reuse')return <><H>候補を残しておくと、別のスタンプにも</H><div style={{display:'flex',gap:20,alignItems:'center'}}><div style={{width:302,border:`2px solid ${theme.border}`}}><Label>C案の椅子ポーズ</Label><Image name="workC" width={298} height={285}/></div><div style={{fontSize:36,color:theme.blue}}>→</div><div style={{width:302,border:`3px solid ${theme.blue}`}}><Label active>「二流」で採用</Label><Animation name="niryuAdopted" frame={mediaFrame} width={296} height={283}/></div></div><Note>椅子をアーロンチュアに変え、別スタンプへ転用</Note></>;
 if(view==='option-compare'){
  const selected=d.id==='options-04'?(after('椅子で')?2:after('パーティション')?1:0):d.id==='options-08'?2:/options-0[67]/.test(d.id)?1:-1;
  return <><H>しっくりこない一個は、構図を変えて3案</H><div style={{display:'flex',gap:12,width:726}}>{[['workA','A　立ち姿'],['workB','B　肘を置く'],['workC','C　ふんぞり返る']].map(([name,label],i)=><div key={name} style={{flex:1,border:`3px solid ${selected===i?theme.blue:'#c9d5ce'}`,background:selected===i?theme.yellow:'white'}}><Label active={selected===i}>{label}</Label><Image name={name} width={229} height={270}/></div>)}</div><Note>{d.id==='options-08'?'椅子の案は、後に別スタンプ「二流」へ転用':selected===1?'「この馴れ馴れしさが欲しかった」と、絵を見て選べる':'第二弾「ちゃんと働いてるか？」の実際の候補'}</Note></>;
 }
 if(view==='redraw-compare'){
  const face=d.id==='redraw-05';
  return <><H>{face?'顔や口は、元のキャラクターも見直す':'構図が決まったら、きれいに描き直す'}</H><div style={{display:'flex',gap:18,width:720}}>{[[face?'redrawBeforeFace':'redrawBefore','構図を詰めた画像'],[face?'redrawAfterFace':'redrawAfter','1枚ずつ描き直し']].map(([name,label],i)=><div key={name} style={{width:351,border:`2px solid ${i?theme.blue:theme.border}`}}><Label active={Boolean(i)}>{label}</Label><Image name={name} width={347} height={282}/></div>)}</div><Note>{face?'今回の比較：そば屋「おはよう」の採用構図 → 生成し直した原画':'採用画像は構図の見本、元のシートはキャラクターの見本'}</Note></>;
 }
 if(view==='redraw-prompt')return prompt('採用画像と、キャラクター資料を渡す',['この構図とポーズを保って、','一枚ずつきれいに描き直して。','顔や体格は、','元のキャラクターシートも重視して。'],['採用した画像','構図の見本','キャラクター','一緒に']);
 if(view==='pets-sheet'){
  const active=d.id==='pets-02'&&after('これを');const pick=Math.min(5,Math.max(0,Math.floor((local-cue('これを'))/Math.max(1,d.durationInFrames-cue('これを'))*6)));
  return <><H>{d.id==='pets-06'?'動きのコマをまとめた「スプライトシート」':'一枚に、連続した姿勢を描いてもらう'}</H><div style={{position:'relative',width:660,height:350}}><Img src={staticFile(first.sources.yotanSheet)} style={{width:660,height:350,objectFit:'contain'}}/>{active&&<div style={{position:'absolute',left:67.5+(pick%3)*175,top:Math.floor(pick/3)*175,width:175,height:175,border:`4px solid ${theme.blue}`,boxSizing:'border-box'}}><div style={{position:'absolute',left:-2,top:-2,background:theme.blue,color:'white',padding:'3px 7px',fontSize:19}}>{pick+1}コマ目</div></div>}</div><Note>第一弾よーたんの実際の原画 ／ 3列 × 2行</Note></>;
 }
 if(view==='pets-process')return <><H>OpenAI公式のPets用スキルを応用</H><div style={{width:708,border:`2px solid ${theme.blue}`,padding:'12px 18px',boxSizing:'border-box',textAlign:'left',background:theme.yellow}}><b style={{fontSize:25,color:theme.blue}}>Codex Pets用スキル</b><span style={{fontSize:21,marginLeft:20}}>一枚に描く → 切り出す → 再生する</span></div><div style={{display:'flex',alignItems:'center',gap:14,marginTop:20}}><div><Img src={staticFile(first.sources.yotanSheet)} style={{width:300,height:220,objectFit:'contain'}}/><div style={{fontSize:23,color:theme.blue,fontWeight:700}}>連続した姿勢</div></div><div style={{fontSize:36,color:theme.blue}}>→</div><div><Sticker id="yotan" frame={mediaFrame} width={300} height={230}/><div style={{fontSize:23,color:theme.blue,fontWeight:700}}>LINEスタンプに応用</div></div></div><Note>参考スキル・OpenAI公式ページは概要欄へ</Note></>;
 if(view==='pets-prompt')return prompt('手法と、参考にするスキルを伝える',['Codex Pets用スキルの作り方を参考に、','連続した姿勢を1枚のスプライトシートに','生成して、コマごとに切り出して','アニメーションにしたい。'],['一枚の中','連続した姿勢','手法の名前','参考にする']);
 if(view==='acting-sobaya')return <><H>動きは「どう見えてほしいか」を伝える</H><div style={{display:'flex',alignItems:'center',gap:22,width:710}}><Sticker id="sobaya" frame={mediaFrame} width={345} height={310}/><div style={{flex:1,padding:'24px 20px',border:`3px solid ${theme.blue}`,fontSize:31,lineHeight:1.65,textAlign:'left',background:theme.yellow,fontWeight:700,color:theme.blue}}>ビールを<br/>大事そうに<br/>愛でている感じ</div></div><Note>第一弾「酒は友達」</Note></>;
 if(view==='acting-work'){
  const candidate=d.id==='acting-04';
  return <><H>{candidate?'細かく言い直しても、しっくりこない…':'欲しいのは「この先輩の雰囲気」'}</H><div style={{display:'flex',gap:24,alignItems:'center',width:710}}><div style={{border:`2px solid ${theme.border}`}}><Animation name={candidate?'elbowA':'workAdopted'} frame={mediaFrame} width={345} height={305}/><Label active={!candidate}>{candidate?'試作した動き':'採用した動き'}</Label></div><div style={{fontSize:29,lineHeight:1.65,textAlign:'left',color:theme.blue,fontWeight:700,flex:1}}>{d.id==='acting-07'||d.id==='acting-08'?<>指示は雰囲気の参考に<br/><div style={{marginTop:22,paddingTop:17,borderTop:`2px solid ${theme.border}`}}>細かな動きは<br/>絵に合わせて考えて</div></>:<>馴れ馴れしく<br/>絡んでくる、<br/>ちょっとウザい先輩</>}</div></div><Note>第二弾「ちゃんと働いてるか？」</Note></>;
 }
 if(view==='acting-prompt')return prompt('雰囲気 ＋ 譲れないところを伝える',['馴れ馴れしい先輩が、軽く覗き込んでくる感じ。','細かな動きは絵に合うように考えて。','動きや間の違う案を3つ見せて。'],['最後は','そのうえで','雰囲気']);
 if(view==='acting-options')return <><H>{d.id==='acting-13'?'全部しっくりこなければ、伝え直してよい':'動きも、候補を並べて見比べる'}</H><div style={{display:'flex',gap:12,width:726}}>{['elbowA','elbowB','elbowC'].map((name,i)=><div key={name} style={{flex:1,border:`2px solid ${theme.border}`}}><Label>動きの案 {['A','B','C'][i]}</Label><Animation name={name} frame={mediaFrame} width={233} height={261}/><div style={{fontSize:20,padding:'9px 5px',color:theme.muted}}>今回はこちらは不採用</div></div>)}</div><Note>{d.id==='acting-13'?'この3案からは選ばず、欲しい雰囲気を伝え直した':'第二弾で実際に比較した、肘と体重移動の3案'}</Note></>;
 if(view==='inspect-history-white'||view==='inspect-history-black'){
  const dark=view==='inspect-history-black';
  return <><H>{dark?'同じ書き出し画像を、黒背景にすると…':'第一弾で実際に起きた、透過の失敗'}</H><div style={{display:'flex',gap:22,alignItems:'center',width:710}}><div style={{width:440,border:`2px solid ${dark?theme.blue:theme.border}`}}><Label active={dark}>{dark?'背景だけ黒に切り替え':'修正前・白背景で確認'}</Label><div style={{background:dark?'#101417':'white',height:315,display:'flex',alignItems:'center',justifyContent:'center'}}><Image name="historySobayaBefore" width={380} height={310}/></div></div><div style={{flex:1,fontSize:27,lineHeight:1.75,textAlign:'left',color:theme.blue,fontWeight:700}}>{dark?<>文字の穴に白残り<br/>髪・ジョッキの<br/>輪郭がギザギザ</>:<>明るい背景では<br/>気づきにくかった<br/>消し残し</>}</div></div><Note>Gitに残っていた修正前の完成APNG ／ 同じ先頭フレーム</Note></>;
 }
 if(view==='inspect-history-report')return <><H>実際の登録後に、暗い背景で発覚</H><div style={{display:'flex',alignItems:'center',gap:24,width:710}}><Image name="historyReport" width={468} height={355}/><div style={{flex:1,textAlign:'left',fontSize:26,lineHeight:1.75,color:theme.blue}}><b>当時の報告画像</b><div style={{fontSize:22,marginTop:20,color:theme.muted}}>2026年10月14日<br/>透過処理を見直す<br/>きっかけに</div></div></div><Note>当時添付されたスクリーンショットを、無加工で使用</Note></>;
 if(view==='inspect-whiteblack'||(view==='inspect-details'&&(d.id==='inspect-06'||!after('文字の穴')||after('完成品')))){
  const dark=Math.floor(mediaFrame/100)%2===1;
  return <><H>完成品を、白と黒の両方で確認</H><div style={{display:'flex',width:715,gap:10,marginBottom:10}}>{[false,true].map(x=><div key={String(x)} style={{fontSize:23,fontWeight:700,padding:'7px 23px',background:dark===x?theme.blue:'#eff4f0',color:dark===x?'white':theme.blue,border:`2px solid ${dark===x?theme.blue:theme.border}`}}>{x?'黒背景':'白背景'}</div>)}</div><FirstGrid frame={mediaFrame} dark={dark}/><Note>{dark?'白い消し残し・服の欠け・輪郭を確認':'修正後の同じ完成スタンプを、背景色だけ変えて確認'}</Note></>;
 }
 if(view==='inspect-details')return <><H>消し残しと、消しすぎの両方を見る</H><div style={{display:'flex',gap:12,width:720}}>{[['historyLetterBefore','文字の穴の白残り'],['historyHairBefore','髪の輪郭の白残り'],['historyShirtBefore','白い服まで欠ける']].map(([name,label])=><div key={name} style={{width:232,border:`2px solid ${theme.border}`}}><div style={{fontSize:22,fontWeight:700,padding:'11px 4px',color:theme.blue,background:'#eff4f0'}}>{label}</div><div style={{height:210,display:'flex',alignItems:'center',background:'#101417'}}><Image name={name} width={228} height={202} style={{imageRendering:'pixelated'}}/></div></div>)}</div><Note>実際の修正前APNGから拡大 ／ 白Tシャツ・顔・ビールの泡は残す</Note></>;
 if(view==='inspect-prompt')return prompt('確認用GIFも、まとめて頼める',['完成した8個を並べた確認用GIFを、','白背景と黒背景でそれぞれ作って。'],['アニメーション','一覧']);
 if(view==='tools-beforeafter')return <><H>背景の細かな修正は、画像処理で</H><div style={{display:'flex',gap:18,width:720}}>{[['historySobayaBefore','実際の修正前'],['historySobayaAfter','画像処理で修正後']].map(([name,label],i)=><div key={name} style={{width:351,border:`2px solid ${i?theme.blue:theme.border}`}}><Label active={Boolean(i)}>{label}</Label><div style={{height:250,background:'#101417',display:'flex',alignItems:'center',justifyContent:'center'}}><Image name={name} width={296} height={250}/></div></div>)}</div><div style={{display:'flex',gap:18,marginTop:14,width:720}}>{['OpenCV','ImageMagick'].map(name=><div key={name} style={{flex:1,padding:'7px 15px',fontSize:28,fontWeight:700,color:theme.blue,border:`2px solid ${theme.blue}`,background:theme.yellow}}>{name}</div>)}</div><Note>文字の細い白フチは、暗い背景で読めるよう意図的に残す</Note></>;
 if(view==='tools-choice'){
  if(['tools-07','tools-07b','tools-07c'].includes(d.id))return <><H>白を全部消すと、服も消えてしまう</H><div style={{display:'flex',alignItems:'center',gap:18}}><div style={{border:`2px solid ${theme.border}`,background:'#111'}}><Sticker id="sobaya" frame={mediaFrame} width={340} height={310}/></div><div style={{textAlign:'left',fontSize:28,lineHeight:1.7}}><div style={{color:theme.alert,fontWeight:700,marginBottom:18}}>消す：背景・文字の穴</div><div style={{color:theme.blue,fontWeight:700}}>残す：白Tシャツ<br/>　　　顔・ビールの泡</div></div></div><Note>背景と、絵の中の白を分けて処理する</Note></>;
  const active=d.id==='tools-06'?(after('今の絵')?1:0):d.id==='tools-08'?1:-1;
  return <><H>絵を変える？　今の絵を整える？</H><div style={{display:'flex',gap:17,width:720}}>{[['Imagegen','新しいポーズを描く','構図を変える'],['OpenCV ＋ ImageMagick','背景の残りを消す','今の絵を保って整える']].map(([name,...lines],i)=><div key={name} style={{width:351,border:`3px solid ${active===i?theme.blue:theme.border}`,textAlign:'left',background:active===i?theme.yellow:'white'}}><div style={{fontSize:i===0?31:25,fontWeight:750,color:theme.blue,padding:'18px 17px',borderBottom:`1px solid ${theme.border}`}}>{name}</div><div style={{fontSize:27,padding:'25px 17px',lineHeight:1.9}}>{lines.map(line=><div key={line}>{line}</div>)}</div></div>)}</div><Note>直したい内容に合わせて、ツールを伝え分ける</Note></>;
 }
 if(view==='tools-prompt')return prompt('今の絵を保ったまま、消し残しを修正',['キャラクターは描き直さず、','背景の消し残しを修正して。','OpenCVやImageMagickを使って、','白い服や泡は残して。','修正後は白黒両方の背景で見せて。']);
 if(view==='closing-flow'){
  if(d.id==='close-03')return <><H>窓際族スタンプ第一弾、販売中</H><FirstGrid frame={mediaFrame}/><Note>申請担当：そば屋さん ／ スタンプ・参考スキルは概要欄へ</Note></>;
  const step=d.id==='close-01'?0:after('白黒')?3:after('動きは')?2:after('描き直して')?1:0;
  return <><H>並べて、見て選びながら作る</H><div style={{width:705,display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:15}}>{[['1','8個まとめて案出し','候補を並べて選ぶ'],['2','きれいな原画にする','構図 ＋ キャラクター資料'],['3','動きの雰囲気を伝える','複数案を比べる'],['4','白と黒で確認','画像処理で整える']].map(([n,title,detail],i)=><div key={n} style={{textAlign:'left',padding:'22px 19px',border:`3px solid ${step===i?theme.blue:theme.border}`,background:step===i?theme.yellow:'white'}}><div style={{fontSize:26,fontWeight:750,color:theme.blue,marginBottom:12}}>{n}. {title}</div><div style={{fontSize:23}}>{detail}</div></div>)}</div></>;
 }
 if(view==='ending')return <><H>ごめんやで</H><Sticker id="yametaro" frame={mediaFrame} width={420} height={355}/></>;
 return null;
};
