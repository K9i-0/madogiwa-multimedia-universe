import React from 'react';
import {Img,OffthreadVideo,staticFile,Loop} from 'remotion';
import {ModelScene} from './ModelScene';
const green='#176B47',ink='#182F24';
const Pic=({src,h=350,w=720}:{src:string;h?:number;w?:number})=><Img src={staticFile(src)} style={{width:w,height:h,objectFit:'contain'}}/>;
const Title=({children}:{children:React.ReactNode})=><div style={{fontSize:29,fontWeight:700,color:green,marginBottom:15}}>{children}</div>;
const Note=({children}:{children:React.ReactNode})=><div style={{fontSize:18,color:'#485c50',marginTop:10,lineHeight:1.45}}>{children}</div>;
const Boxes=({items,active=0}:{items:string[];active?:number})=><div style={{display:'flex',gap:12,width:'100%',justifyContent:'center'}}>{items.map((s,i)=><div key={s} style={{flex:1,padding:'22px 10px',border:`2px solid ${i===active?green:'#a7b8ad'}`,background:i===active?'#e0f0e5':'#fff',fontSize:25,lineHeight:1.65,whiteSpace:'pre-line'}}>{s}</div>)}</div>;
const costViews=['cost','cost_video','cost_tripo','cost_total'];
export function Visual({view,t}:{view:string;t:number}){
 if(['sobaya_intro','sobaya_raw','greeting','walk','rig','three','remotion','ending'].includes(view)){
 const mode=view==='walk'?'walk':view==='rig'||view==='greeting'?'greeting':view==='remotion'?(t%12<6?'greeting':'walk'):'turn';
 return <><Title>{view==='rig'?'骨格 ＋ 表面への影響':view==='three'?'Three.jsでGLBを表示':view==='remotion'?'同じモデルで、カメラと動作を変える':'そば屋 ｜ Tripo原型から仕上げたモデル'}</Title><ModelScene t={t} mode={mode} bones={view==='rig'} close={view==='remotion'&&t%12>=6}/><Note>{view==='remotion'?'Remotionのフレーム番号 → 時刻 → モデルの姿勢':view==='rig'?'リグ：動かす仕組み　／　ウェイト：表面への影響':'実際の採用GLBをThree.jsで表示'}</Note></>;
 }
 if(['takosan_intro','tako_bones'].includes(view))return <><Title>{view==='tako_bones'?'たこさんの触手 ｜ 6本 × 3関節':'たこさん ｜ 採用済みの浮遊'}</Title><ModelScene kind="takosan" t={t} bones={view==='tako_bones'} mode="float"/><Note>手付けの動作と、コードで関節を動かす処理</Note></>;
 if(view==='fuku')return <><Title>実写の人物は「本人らしさ」が難しい</Title><div style={{display:'flex',alignItems:'center'}}><div style={{width:240,height:340,overflow:"hidden",position:"relative"}}><Img src={staticFile("fuku_photo.jpg")} style={{position:"absolute",height:730,width:440,objectFit:"contain",left:-100,top:-12}}/></div><ModelScene kind="fukuchan" t={t} mode="face" close width={480} height={340}/></div><Note>福ギュン：顔の立体感・肌・髪を生成後に調整</Note></>;
 if(view==='old')return <><Title>ワイが作ってもらった、そば屋さん</Title><Pic src="old.jpg" h={365}/><Note>Blenderで作ったそば屋</Note></>;
 if(view==='sheet')return <><Title>まず、キャラクターの基準を決める</Title><Pic src="sheet.png" h={370}/><Note>顔 ／ 体格 ／ 衣装 ／ 後ろ姿</Note></>;
 if(['turn','portrait'].includes(view))return <><Title>{view==='portrait'?'全身を大きく、細部を残す':'Wanで生成した実際の回転動画'}</Title><div style={{display:'flex',alignItems:'center',gap:25}}><Loop layout="none" durationInFrames={240}><OffthreadVideo muted src={staticFile('turn.mp4')} style={{height:350,width:263,objectFit:'contain'}}/></Loop><div style={{width:370,textAlign:'left',fontSize:26,lineHeight:1.8}}>{view==='portrait'?<>縦 832 × 1108<br/>8秒・720P設定<br/><span style={{fontSize:20}}>今回の制作例の設定</span></>:<>向きを連続して確認<br/>顔・服・全身の見切れ<br/><span style={{fontSize:20}}>動画でも形は変わり得る</span></>}</div></div></>;
 if(view==='views')return <><Title>時刻ではなく、向きを見て選ぶ</Title><div style={{display:'flex',gap:9}}>{['front','left','back','right'].map((v,i)=><div key={v}><Pic src={`sobaya_${v}.png`} w={168} h={290}/><div style={{fontSize:23,marginTop:8}}>{['正面 0.2秒','左 2.5秒','背面 4.0秒','右 5.6秒'][i]}</div></div>)}</div><Note>実際にTripoへ渡した4枚・近似角度</Note></>;
 if(view==='config')return <><Title>実際の設定ファイルから、画像を指定</Title><pre style={{width:660,textAlign:'left',padding:'22px 28px',fontSize:23,lineHeight:1.65,background:'#eff4f0',border:'1px solid #a7b8ad',margin:0}}>{`images
  front: inputs/front.png
  left:  inputs/left.png
  back:  inputs/back.png
  right: inputs/right.png
generation.model: P2-20260801`}</pre><Note>そば屋の制作当時の設定を抜粋<br/>tools/tripo_multiview.py から送信</Note></>;
 if(view==='tako_views')return <><Title>たこさんは、正面と背面の2枚</Title><div style={{display:'flex',gap:25}}><Pic src="takosan_front.png" w={300}/><Pic src="takosan_back.png" w={300}/></div><Note>シートから用意した入力画像</Note></>;
 if(view==='wan_link')return <><Title>Wanを使った動画づくりは、こちら</Title><Pic src="wan_thumbnail.png" h={330}/><Note>公開済み「AI動画制作の解説」｜ 概要欄にリンク</Note></>;
 if(view==='website')return <><Title>公式サイトで、実際に触れます</Title><Loop layout="none" durationInFrames={720}><OffthreadVideo muted src={staticFile('site_demo.mp4')} style={{width:720,height:370,objectFit:'contain'}}/></Loop><Note>madogiwa.work/characters/sobaya　｜　概要欄から</Note></>;
 if(view==='ar')return <><Title>AR：いつもの空間に、キャラクターを</Title><Pic src="ar.png" h={350}/><Note>公式サイトのAR入口・対応するiPhone／Safariで利用</Note></>;
 if(view==='game')return <><Title>Flutter Sceneで、ゲームにも</Title><Pic src="game.png" h={370}/><Note>「そば屋ハザード」実際のゲーム画面（保存済み画像）</Note></>;
 if(view==='weights')return <><Title>動かして分かった、曲がり方の問題</Title><Pic src="weights.png" h={330}/><Note>保存済みの挨拶・上腕ウェイト修正比較</Note></>;
 if(view==='face_fix'||view==='blender')return <><Title>{view==='blender'?'Codex ＋ Blenderで手直し':'仮面・光沢・姿勢を整える'}</Title><div style={{display:'flex',gap:15}}><div><Pic src="posture_before.png" w={330} h={330}/><div>姿勢修正前</div></div><div><Pic src="posture_after.png" w={330} h={330}/><div>姿勢修正後</div></div></div><Note>実際の制作時に保存した同視点の比較</Note></>;
 if(costViews.includes(view)){const idx=costViews.indexOf(view);return <><Title>今回のそば屋・生成費用の例</Title><div style={{width:680,fontSize:29,textAlign:'left'}}>{[['回転動画','$0.56 ≒ 90円'],['Tripo生成','120 credits ≒ 192円'],['この2工程の合計','約282円']].map(([a,b],i)=><div key={a} style={{display:'flex',justifyContent:'space-between',padding:'23px 16px',borderBottom:'1px solid #a7b8ad',background:idx===i+1?'#e0f0e5':'white',fontWeight:i===2?700:400}}><span>{a}</span><span>{b}</span></div>)}</div><Note>1ドル160円の固定換算／動画は制作記録の推定費用<br/>入力画像・再試行・Codex等の利用料は別</Note></>;}
 const contents:Record<string,{title:string;items:string[];note?:string}>={
 opening:{title:'画像から、3Dキャラクターへ',items:['画像を用意','立体を生成','動かして使う'],note:'窓際族物語の実際の制作例'},
 tripo:{title:'Tripo：画像や文章から3Dを生成',items:['参照画像','Tripo','形 ＋ 色'],note:'今回紹介するのは、画像からのキャラクター制作'},
 cost_time:{title:'追加料金と、制作にかかるコスト',items:['サービス代','試行回数','確認する時間'],note:'汎用モデルだけで挑戦する面白さもある'},
 roles:{title:'得意なところを、組み合わせる',items:['Tripo\n原型を生成','Codex＋Blender\n修正・仕上げ','コード\n表示・組み込み']},
 hosts:{title:'窓際族物語の3D制作ノート',items:['やめ太郎\n試したい人','たこさん\n制作を紹介'],note:'そば屋・たこさんの実例と、福ギュンの難しさ'},
 pipeline:{title:'一体が動くまでの流れ',items:['参照画像\n回転動画','Tripo\n3D生成','Blender\n修正・リグ','Web・動画\nAR・ゲーム']},
 plans:{title:'StudioとAPIは、別の使い方',items:['Studio\nブラウザで操作\n月額・年額プラン','API\nコードから利用\n購入クレジットを消費'],note:'契約・クレジットは別／たくさん作るならプランも比較'},
 api:{title:'窓際族物語ではAPIを利用',items:['必要なときに生成','使った処理に応じて消費','Codexから呼び出す'],note:'クレジットを事前購入する方式'},
 agents:{title:'Codex専用ではありません',items:['Codex','Claude Code','Cursor'],note:'Tripo公式にも3つのエージェントからの利用案内'},
 consistency:{title:'別々の画像で、姿が変わることも',items:['正面の顔','側面の体格','背面の服'],note:'回転動画でつながりを確認／完全な一貫性の保証ではない'},
 video_models:{title:'回転動画は、使い慣れた方法で',items:['今回：Wan','他の選択肢\nMiniMax H3など'],note:'Wanの操作手順は公開済み解説へ'},
 config:{title:'入力画像と設定をファイルに残す',items:['front / left\nback / right','生成モデル\n面数・材質','Pythonから\nTripoへ送信'],note:'実装：tools/tripo_multiview.py'},
 tasks:{title:'生成を送ったら、番号で追う',items:['submit\n生成を依頼','status\n進み具合を確認','download\n結果を取得'],note:'送信記録で重複生成を防ぐ'},
 tako_fix:{title:'たこさんの生成後に直したこと',items:['生成時：8本','デザイン：6本','配置・手・内張り'],note:'生成後に、キャラクターの特徴へ合わせる'},
 uses:{title:'同じモデルから、使い道が広がる',items:['Webサイト','動画','AR','ゲーム'],note:'表示するだけから、操作・演技・ゲームの処理へ'},
 links:{title:'実物と制作手順は、概要欄から',items:['公式サイト\n3Dを触る','Wan解説\n動画を作る','GitHub\n制作手順を見る'],note:'madogiwa.work　／　Madogiwa Multimedia Universe'},
 };
 const c=contents[view]??contents.pipeline;return <><Title>{c.title}</Title><Boxes items={c.items} active={-1}/>{c.note&&<Note>{c.note}</Note>}</>;
}
