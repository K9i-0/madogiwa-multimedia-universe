import React from 'react';

type Insert={kind:string;from:number;to:number;changeFrame:number};
export const WorkInsert:React.FC<{item:Insert;frame:number}>=({item,frame})=>{
 const local=frame-item.from,changed=frame>=item.changeFrame;
 const excel=item.kind.startsWith('excel');
 let open=true;
 if(item.kind==='excel')open=local%100<72;
 if(item.kind==='excel-village')open=frame<item.changeFrame+38;
 if(item.kind==='excel-return')open=!(frame>=item.changeFrame&&frame<item.changeFrame+42);
 if(!open)return null;
 const title=excel?'業務報告.xlsx':item.kind==='bad-ui'?'点検結果の入力':item.kind==='password'?'社内ログイン':item.kind==='bug-report'?'不具合の報告':item.kind==='inspection'?'施設破損報告書':'飲酒記録.xlsx';
 const body:React.CSSProperties={background:'#d0cfc5',color:'#252722',padding:'28px 40px',height:300};
 const cell:React.CSSProperties={border:'1px solid #858a80',padding:'13px 20px',fontSize:26};
 return <div style={{position:'absolute',left:190,right:190,top:92,fontFamily:'Hiragino Kaku Gothic ProN, sans-serif',boxShadow:'0 12px 50px #000b',opacity:Math.min(1,local/6)}}>
  <div style={{height:44,background:excel?'#324a3d':'#343a38',color:'#e4e4db',display:'flex',alignItems:'center',padding:'0 20px',fontSize:20}}>{title}<span style={{marginLeft:'auto',fontSize:26}}>−　□　×</span></div>
  <div style={body}>
   {excel&&<>
    <div style={{fontSize:17,borderBottom:'1px solid #92978d',paddingBottom:12,marginBottom:16}}>ファイル　　ホーム　　挿入　　表示</div>
    <div style={{display:'grid',gridTemplateColumns:'50px repeat(4,1fr)',fontSize:21}}>
     {['','A','B','C','D',...Array.from({length:4},(_,i)=>[`${i+1}`,'','','','']).flat()].map((s,i)=><div key={i} style={{height:43,border:'1px solid #a3a69b',background:i<5||i%5===0?'#b6bcb0':'#e2e2d8',textAlign:'center',paddingTop:6,boxShadow:i===6?'inset 0 0 0 2px #3e6c4b':undefined}}>{s}</div>)}
    </div>
   </>}
   {item.kind==='bad-ui'&&<>
    <div style={{fontSize:24,marginBottom:22}}>点検結果</div>
    <div style={{height:84,padding:20,border:'1px solid #777c73',background:'#e7e6db',fontSize:28}}>{local<90?'異常なし':''}</div>
    <div style={{marginTop:28,marginLeft:'auto',width:160,padding:12,textAlign:'center',fontSize:28,background:'#58635b',color:'#fff'}}>{changed?'削除':'保存'}</div>
   </>}
   {item.kind==='password'&&<>
    <div style={{fontSize:24,marginBottom:18}}>パスワード</div>
    <div style={{background:'#e7e6db',border:'1px solid #777',padding:22,fontSize:42,letterSpacing:12,fontFamily:'monospace'}}>{changed?'12345':'1234'}</div>
    {changed&&<div style={{marginTop:25,fontSize:22}}>変更しました</div>}
   </>}
   {item.kind==='bug-report'&&<>
    <div style={{fontSize:26,marginBottom:34}}>今月の不具合件数</div>
    <div style={{fontSize:74,textAlign:'center',fontVariantNumeric:'tabular-nums'}}>{changed?'0':'48'}<span style={{fontSize:30,marginLeft:16}}>件</span></div>
   </>}
   {item.kind==='inspection'&&<table style={{width:'100%',borderCollapse:'collapse',marginTop:12}}><tbody>
    <tr><td style={cell}>対象</td><td style={cell}>祠</td></tr>
    <tr><td style={cell}>原因</td><td style={cell}>老朽化による破損</td></tr>
    <tr><td style={cell}>確認</td><td style={cell}>{changed?'○　○　○':''}</td></tr>
   </tbody></table>}
   {item.kind==='drinking-record'&&<table style={{width:'100%',borderCollapse:'collapse'}}><tbody>
    <tr><td style={cell}>日付</td><td style={cell}>本数</td></tr>
    <tr><td style={cell}>一日目</td><td style={cell}>0</td></tr>
    {!changed&&<tr style={{background:'#bab4a5'}}><td style={cell}>二日目</td><td style={cell}>6</td></tr>}
    <tr><td style={cell}>三日目</td><td style={cell}>0</td></tr>
   </tbody></table>}
  </div>
 </div>;
};
