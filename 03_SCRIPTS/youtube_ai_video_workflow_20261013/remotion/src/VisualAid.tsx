import React from 'react';
import {Img,staticFile,interpolate} from 'remotion';
import {VisualAid as Legacy} from './VisualAidLegacy';
import cues from './visual-cues-v7.json';
import {theme, headingStyle, cardStyle} from './theme';
type U={id?:string;startFrame:number;durationInFrames:number};
const blue=theme.blue,navy=theme.ink,grey=theme.muted;
const Head=({children}:{children:React.ReactNode})=><div style={headingStyle}>{children}</div>;
const Small=({children}:{children:React.ReactNode})=><div style={{fontSize:18,color:grey,marginTop:22,lineHeight:1.7}}>{children}</div>;
const Pic=({name,h=390}:{name:string;h?:number})=><Img src={staticFile(name)} style={{width:710,height:h,objectFit:'contain'}}/>;
const Tiles=({labels,focus=-1,shown=99}:{labels:string[];focus?:number;shown?:number})=><div style={{display:'flex',width:710,gap:20}}>{labels.map((s,i)=><div key={s} style={cardStyle(i===focus||focus<0,i<=shown)}>{s}</div>)}</div>;
// Reuse audited drawings; each mapping explicitly names the legacy visual state.
const reuse:Record<number,[string,string]>={
 13:['intro_reaction','u002'],14:['intro_reaction','u002'],27:['environment','u018'],28:['environment','u018'],
 29:['prompt_model','u026'],30:['prompt_model','u026'],31:['prompt_evidence','u025'],32:['prompt_evidence','u024'],33:['prompt_evidence','u025'],34:['prompt_model','u028'],35:['prompt_model','u028'],36:['prompt_model','u029'],37:['human_review','u020'],38:['human_review','u020'],
 39:['sheet_identity','u032'],40:['fuku_sheet','u033'],41:['sheet_identity','u034'],42:['sheet_identity','u034'],43:['faceless','u035'],44:['faceless','u036'],45:['faceless','u037'],46:['faceless','u038'],47:['ref_roles','u039'],48:['ref_roles','u040'],49:['voice_sources','u042'],50:['voice_sources','u043'],51:['voice_sources','u044'],52:['voice_problem','u045'],53:['voice_problem','u046'],54:['news_patch','u047'],55:['patch_cost','u049'],56:['patch_cost','u050'],57:['park_intro','u051'],58:['park_method','u052'],59:['park_method','u053'],60:['sync','u054'],61:['offscreen','u055'],62:['offscreen','u056'],63:['news_before','u057'],64:['news_before','u057'],69:['news_after','u059'],70:['news_after','u059'],71:['edit_demo','u060'],72:['edit_demo','u061'],73:['edit_demo','u062'],74:['repair','u063'],75:['repair','u064'],83:['resolution','u073'],84:['highres','u077'],85:['highres','u077'],86:['choice','u074'],87:['choice','u075'],88:['choice','u076'],89:['logs','u083'],90:['skill_intro','u085'],91:['skill_intro','u086'],97:['api_failure','u087'],98:['api_split','u088'],99:['api_split','u089'],100:['validation','u090'],101:['validation','u091'],103:['skill_scope','u095'],104:['skill_scope','u097'],105:['skill_loop','u098'],106:['skill_loop','u099'],107:['skill_loop','u100'],108:['skill_loop','u100'],109:['skill_loop','u100'],112:['first_step','u103'],113:['first_step','u104'],118:['ending','u108'],119:['ending','u109']};
export const VisualAid:React.FC<{view:string;frame:number;utterance?:U}>=({frame,utterance})=>{
 const id=utterance?.id??'v000';const n=Number(id.slice(1));const local=frame-(utterance?.startFrame??0),dur=utterance?.durationInFrames??100;
 const timing=(cues as Record<string,Record<string,number>>)[id]??{};
 const at=(key:string,fallback:number)=>local>=(timing[key]??Math.round(dur*fallback));
 const phase=(keys:string[],ratios:number[])=>keys.filter((k,i)=>at(k,ratios[i])).length;
 if(n<=7||n===12)return <Pic name="news.jpg" h={430}/>;
 if(n===8)return <><Head>動画編集、ほぼ未経験。</Head><Tiles labels={['Web・アプリ\n✓','動画編集\n？']} focus={1}/></>;
 if(n===9||n===10||n===25)return <><Head>Codex / Claude Code</Head><div style={{background:theme.paper,border:`3px solid ${theme.blue}`,borderBottom:`8px solid ${theme.yellow}`,padding:'20px 34px',borderRadius:12,fontSize:36,fontWeight:700,color:navy}}>「ここ直して」</div></>;
 if(n===11){const p=phase(['作り方','かかるお金','失敗'],[.4,.56,.69])-1;return <Tiles labels={['作る','費用','直す']} focus={p} shown={p}/>;}
 if(n>=15&&n<=17)return <><Head>映像を作るモデルも、選べる。</Head><Tiles labels={['指示を考える\nAI','映像を作る\nAI']} focus={1}/></>;
 if(n>=18&&n<=20){const p=n===18?phase(['Alibaba','それから'],[.4,.7]):n===20?1:-1;return <><Head>動画生成モデル</Head><Tiles labels={['Seedance\nByteDance','Wan\nAlibaba','H3\nMiniMax']} focus={p} shown={n===18?p:2}/>{n===20&&<div style={{fontSize:32,color:blue,marginTop:35}}>今回は Wan 3.0</div>}</>;}
 if(n===21||n===22)return <><Head>画面から操作する方法も</Head><div style={{fontSize:47,color:blue}}>Higgsfield</div><Small>使えるモデル・機能はプランによる</Small></>;
 if(n===23||n===24)return <><Head>いつもの会話から、制作へ</Head><Tiles labels={['人間','Codex /\nClaude Code','制作の道具']} focus={n===23?1:2}/><div style={{fontSize:34,marginTop:32,color:blue}}>相談 → 指示 → 実行</div></>;
 if(n===26){const p=at('音声',.3)?1:0;return <><Head>Codex / Claude Code から実行</Head><Tiles labels={['Wan\nAPI','音声・編集\nコード／コマンド']} focus={p}/></>;}
 if(n===32)return <><Pic name="news_mask.jpg" h={340}/><Tiles labels={['体格：福ギュン','仮面：そば屋']} focus={at('0.58',.58)?1:0}/></>;
 if(n===65||n===66)return <><Pic name="news_raw.jpg" h={335}/><div style={{fontSize:32,color:navy,marginTop:20}}>日本語の字幕は、あとから。</div></>;
 if(n===67){const p=phase(['時間','動画に'],[.55,.8]);return <><Head>Remotion</Head><Tiles labels={['Reactで\n画面を作る','時間に合わせて\n変化させる','動画へ\n書き出す']} focus={p} shown={p}/><div style={{width:650,height:60,position:'relative',marginTop:30,borderBottom:`3px solid ${theme.border}`}}><div style={{position:'absolute',left:interpolate(local,[0,dur],[0,600],{extrapolateRight:'clamp'}),color:blue,fontSize:30}}>●</div></div></>;}
 if(n===68)return <><Head>得意な道具で、役割分担</Head><Tiles labels={['Wan\n人物・演技','Remotion\n字幕・テロップ']} focus={!at('映像の演技',.3)||at('正確な字幕',.7)?1:0}/><Small>文字は、指定した文章をフォントで描画</Small></>;
 if(n===76||n===77)return <><Head>動画の生成料金</Head><div style={{fontSize:44,color:blue}}>秒数 × 解像度</div><Small>Qwen Cloud・Wan 3.0</Small></>;
 if(n===78||n===79){const p=n===79?3:phase(['480p','720p','1080p'],[.53,.68,.81])-1;return <><Head>30秒・1回の生成</Head><div style={{display:'flex',alignItems:'flex-end',gap:38,height:285,width:660}}>{[240,480,960].map((v,i)=><div key={v} style={{flex:1,visibility:i>p?'hidden':'visible',borderBottom:`6px solid ${p===3||i===p?theme.yellow:'transparent'}`,paddingBottom:8}}><div style={{fontSize:34,fontWeight:700,marginBottom:12}}>約{v}円</div><div style={{height:v/6,background:blue,borderRadius:'6px 6px 0 0'}}/><div style={{fontSize:27,marginTop:12}}>{['480p','720p','1080p'][i]}</div></div>)}</div><Small>通常価格・1ドル160円換算（概算）</Small></>;}
 if(n===80||n===81)return <><Head>作った分が、制作費。</Head><Tiles labels={['候補1\n240円','候補2\n240円','採用\n240円']}/><div style={{opacity:n===81||at('約720円',.3)?1:0,fontSize:44,marginTop:35,color:navy}}>合計 約720円</div><Small>480p・30秒 × 3回／通常価格・1ドル160円換算</Small></>;
 if(n===82)return <><Head>動画生成のほかにも</Head><Tiles labels={['AIの利用料','音声・編集の\n実行環境']} focus={at('音声',.5)?1:0}/><Small>実際の費用は為替・割引・決済条件等で変わる</Small></>;
 if(n===83)return <><Head>低解像度で試す</Head><Pic name="news_sobaya.jpg" h={260}/>{at('画質',.45)&&<div style={{marginTop:20}}><Tiles labels={['そのまま採用','高解像度で再生成']} focus={1}/></div>}</>;
 if(n===100&&at('条件を',.65))return <Legacy view="validation" frame={local} utterance={{id:'u091',startFrame:0,durationInFrames:dur}}/>;
 if(n===92||n===93)return <><Head>制作ノウハウも、Gitへ</Head><Tiles labels={['スキル','キャラクター\nシート','制作記録']} focus={n===93?-1:phase(['キャラクター','過去エピソード'],[.25,.5])}/><Small>.claude/skills　・　03_SCRIPTS</Small></>;
 if(n===94||n===95)return <><Head>記録を、次の制作へ</Head><Tiles labels={['変更を残す','AIが読む','次に生かす']} focus={n===95?-1:phase(['次の制作','会話で'],[.35,.65])}/><div style={{fontSize:25,marginTop:35,color:grey}}>Gitの履歴 ＋ 制作記録</div></>;
 if(n===96)return <><div style={{width:710,height:365,overflow:'hidden',borderRadius:10,position:'relative'}}><Img src={staticFile('repository_public_v7.png')} style={{position:'absolute',width:710,left:0,top:-84}}/></div><div style={{fontSize:22,color:blue,marginTop:22}}>github.com/K9i-0/madogiwa-multimedia-universe</div><Small>公開中・概要欄にリンク</Small></>;
 if(n===102)return <Legacy view="skill_reuse" frame={local} utterance={{id:at('モデルを比較',.53)?'u094':'u093',startFrame:0,durationInFrames:dur}}/>;
 if(n===110||n===111){const p=n===111?4:phase(['Wan','必要な声','Remotion'],[.3,.48,.65]);return <><Head>いつものAIに相談して、一本へ</Head><Tiles labels={['Wan\n映像','Irodori\n必要な声','Remotion\n仕上げ']} focus={n===111?-1:p-1} shown={p===0?-1:p===4?2:p-1}/></>;}
 if(n>=114&&n<=117)return <><Small>次回予告</Small><Head>MiniMax H3</Head>{n===114?<div style={{fontSize:29,color:blue}}>同僚が実践する、もう一つの作り方</div>:n===117?<Tiles labels={['費用','待ち時間','準備・作業']} focus={!at('実際の費用',.5)?-1:phase(['待ち時間','必要な作業'],[.7,.82])}/>:<><Tiles labels={['自分のGPU','ColabのGPU']} focus={n===116?-1:at('Colab',.6)?1:0}/><Small>対応するGPU環境が必要</Small></>}</>;
 const state=reuse[n];if(!state)throw Error('Missing v7 visual '+id);
 // Legacy cues are translated from v7 narration, never inherited from old audio.
 const localCues=(cues as Record<string,Record<string,number>>)[id]??{};
 return <Legacy view={state[0]} frame={local} utterance={{id:state[1],startFrame:0,durationInFrames:dur}} cueOverride={localCues}/>;
};
