import React from 'react';
import {Img,staticFile} from 'remotion';
import views from './views.json';
import {Evidence} from './Evidence';
const gold='#c9b682';
const Head:React.FC<{children:React.ReactNode}>=({children})=><div style={{fontSize:30,letterSpacing:2,lineHeight:1.5,marginBottom:18,fontFamily:'"Hiragino Mincho ProN",serif'}}>{children}</div>;
const Diagram:React.FC<{items:string[];label?:string}>=({items,label})=><div style={{height:360,width:780,display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',gap:22}}>{label&&<div style={{fontSize:18,letterSpacing:4,color:'#99aaa9'}}>{label}</div>}{items.map((s,i)=><div key={s} style={{fontSize:items.length>3?26:31,color:i===items.length-1?gold:'#e6e5df',lineHeight:1.4,whiteSpace:'pre-line',textAlign:'center',borderBottom:'1px solid #c9b68233',padding:'12px 20px',minWidth:540}}>{s}</div>)}</div>;
const Silhouette:React.FC<{labels?:boolean;head?:boolean}>=({labels=false,head=false})=><div style={{height:360,width:780,background:'radial-gradient(ellipse at center,#b3b9ad,#798278)',position:'relative',overflow:'hidden'}}><Img src={staticFile('sobaya_silhouette_v2.png')} style={{position:'absolute',height:head?820:360,left:head?-40:270,top:head?-20:0}}/>{labels&&<><div style={{position:'absolute',top:85,left:30,fontSize:24,color:'#172018'}}>幅広い肩 ─────</div><div style={{position:'absolute',top:180,right:30,fontSize:24,color:'#172018'}}>──── 太い腕</div><div style={{position:'absolute',bottom:35,left:30,fontSize:19,color:'#172018'}}>目撃証言による輪郭再構成</div></>}{head&&<div style={{position:'absolute',right:40,top:145,fontSize:24,color:'#172018',textAlign:'left',lineHeight:1.8}}>仮面状の顔面構造<br/>材質・機能は不明</div>}</div>;
const evidence:Record<string,[string,boolean,boolean?,number?]>={witness:['witness',true],news:['witness',true,true],enhance:['witness',false,true,8],gate:['gate',false,true],window_clue:['gate',false,true],ritual_dark:['ritual',false],waiting_dark:['ritual',false,true],amber:['amber',true],ruins:['ruins',false,true],sleepers:['ruins',false,true],power:['ruins',false,true],hologram:['hologram',false],awakening:['awakening',true],orbital:['orbital',false],swim_dark:['orbital',false],orbital_gift:['gift',false]};
export const Panel:React.FC<{view:string;elapsed:number;start:number}>=({view,start})=>{
 const v=views[view as keyof typeof views];const e=evidence[view];
 const photo=(name:string,width=780,height=360)=><Img src={staticFile(`${name}.jpg`)} style={{width,height,objectFit:'contain'}}/>;
 if(view==='title')return <><div style={{fontSize:17,letterSpacing:7,color:gold,marginBottom:35}}>未知を、記録する。</div><div style={{fontFamily:'"Hiragino Mincho ProN",serif',fontSize:54,lineHeight:1.7}}>めたんの<br/>ミステリー研究所</div><div style={{width:100,height:1,background:gold,margin:'30px auto'}}/></>;
 return <><Head>{v.heading}</Head>
 {['silhouette','outline','mask'].includes(view)&&<Silhouette labels={view==='outline'} head={view==='mask'}/>}
 {e&&<Evidence name={e[0]} handheld={e[1]} still={e[2]} zoom={e[3]} start={start}/>}
 {view==='height'&&<Diagram label="広域未確認生物研究所・測定報告" items={['大型画面で見る → 大きく見える','小型画面で見る → 小さく見える','推定身長：測定環境に依存']}/>}
 {view==='cryptids'&&<div style={{height:360,display:'flex',alignItems:'center',gap:34}}>{[['ビッグフット','北米の伝承'],['イエティ','ヒマラヤの伝承'],['SOBAYA','マドギワの目撃記録']].map(([name,note])=><div key={name} style={{width:230,padding:'30px 0',borderTop:`1px solid ${gold}`,borderBottom:`1px solid ${gold}`}}><div style={{fontFamily:'serif',fontSize:30,color:gold}}>{name}</div><div style={{fontSize:20,marginTop:25}}>{note}</div></div>)}</div>}
 {view==='hair'&&<Diagram label="研究上の解釈" items={['体毛が見えない','↓','非常に短い毛である可能性']}/>}
 {view==='lineage'&&<Diagram label="各専門家が支持する仮説" items={['絶滅原人の残存集団','未知の類人猿','旧文明の末裔']}/>}
 {view==='portal'&&<Diagram label="狭間文明研究所・追試報告" items={['こちら側　→　四角い枠　→　向こう側','研究員 A：移動に成功','研究員 B：同じ結果を確認']}/>}
 {view==='dating'&&<Diagram label="年代決定の根拠" items={['研究班が来る前から、存在していた','↓','古い施設である可能性']}/>}
 {view==='consensus'&&<Diagram label="統合理論" items={['原人説 ＋ 旧文明説 ＋ 地球外起源説','↓','地球外に起源を持つ、旧文明の原人']}/>}
 {view==='new_document'&&<Diagram label="予期しなかった外部からの情報" items={['特番の視聴者','↓','人事部から研究所へ連絡']}/>}
 {view==='answer'&&<div style={{height:360,display:'flex',alignItems:'center',fontFamily:'serif',fontSize:65,color:gold}}>「うちの社員です」</div>}
 {view==='employee'&&<div style={{height:360,display:'flex',alignItems:'center',gap:28}}>{photo('sobaya',355,360)}<div style={{textAlign:'left'}}><div style={{fontSize:22}}>アクシデンチュア</div><div style={{fontSize:48,color:gold,margin:'18px 0'}}>窓際社員</div><div style={{fontSize:36}}>そば屋</div><div style={{fontSize:20,color:'#aab4b7',marginTop:22}}>SOBAYA → そば屋</div></div></div>}
 {view==='corrections'&&<div style={{height:360,display:'flex',alignItems:'center',gap:20}}><div>{photo('lab',375,240)}<div style={{fontSize:23,color:gold,marginTop:15}}>遺跡 → クローン研究施設</div></div><div>{photo('window',375,240)}<div style={{fontSize:23,color:gold,marginTop:15}}>古代の門 → アルミサッシ</div></div></div>}
 {view==='research_response'&&<Diagram label="訂正発表と続報" items={['研究所：社員説も排除していなかった','報道：独自のつながりで正体を解明']}/>}
 {view==='space_question'&&photo('spacebeer')}
 {view==='closing'&&<div style={{height:360,display:'flex',alignItems:'center',fontSize:40,lineHeight:1.9,fontFamily:'serif'}}>研究費の精算は、<br/>今後の課題である。</div>}
 <div style={{fontSize:19,color:'#b0babd',marginTop:17,lineHeight:1.5}}>{v.note}</div>
 </>;
};
