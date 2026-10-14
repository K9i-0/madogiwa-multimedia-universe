import React from 'react';
const GREEN='#176B47';
const tabs=['はじめに','AIの役割','プロンプト','キャラクター','音声','編集','費用','改善ログ','まとめ'];
export const SpreadsheetFrame:React.FC<{chapter?:string;children:React.ReactNode}>=({chapter,children})=>{
 const section=Math.max(0,Number(chapter?.split('.')[0]??1)-1);
 return <>
  <div style={{position:'absolute',inset:0,background:'#fff'}}/>
  <div style={{position:'absolute',left:34,right:0,top:94,bottom:35,backgroundImage:'linear-gradient(to right,#e8ecea 1px,transparent 1px),linear-gradient(to bottom,#e8ecea 1px,transparent 1px)',backgroundSize:'155.75px 58px'}}/>
  <div style={{position:'absolute',left:0,right:0,top:0,height:36,background:GREEN,color:'#fff',display:'flex',alignItems:'center',padding:'0 20px',fontSize:18,fontWeight:600}}>窓際族物語 <span style={{opacity:.5,margin:'0 15px'}}>/</span> AI動画制作ノート<span style={{marginLeft:'auto',fontSize:14,fontWeight:400}}>やめ太郎 ＆ たこさん</span></div>
  <div style={{position:'absolute',left:0,right:0,top:36,height:33,background:'#f6f7f6',borderBottom:'1px solid #bfcac3',display:'flex',alignItems:'center',fontSize:17}}><div style={{width:105,textAlign:'center',borderRight:'1px solid #c9d1cc',color:'#4b5850'}}>B3:H10</div><div style={{width:45,textAlign:'center',fontFamily:'Georgia',fontStyle:'italic',color:'#6b7770'}}>fx</div><div style={{color:'#263c30'}}>{chapter??'1. いつものCodexで、動画も作れる？'}</div></div>
  <div style={{position:'absolute',left:34,right:0,top:69,height:25,display:'flex',background:'#edf1ee',borderBottom:'1px solid #cbd4ce'}}>{'ABCDEFGH'.split('').map(c=><div key={c} style={{flex:1,textAlign:'center',fontSize:14,color:'#5d6d62',borderRight:'1px solid #d1dad4'}}>{c}</div>)}</div>
  <div style={{position:'absolute',left:0,top:94,bottom:35,width:34,background:'#edf1ee',borderRight:'1px solid #cbd4ce'}}>{Array.from({length:11},(_,i)=><div key={i} style={{height:58,textAlign:'center',paddingTop:18,boxSizing:'border-box',fontSize:14,color:'#5d6d62'}}>{i+1}</div>)}</div>
  {children}
  <div style={{position:'absolute',left:0,right:0,bottom:0,height:35,background:'#f0f3f1',borderTop:'1px solid #bccbc1',display:'flex',alignItems:'stretch',paddingLeft:35,gap:0}}>{tabs.map((label,i)=><div key={label} style={{fontSize:16,padding:'6px 19px',background:section===i?'#fff':'transparent',color:section===i?GREEN:'#5a655f',fontWeight:section===i?700:400,borderRight:'1px solid #d6dfd9',borderBottom:section===i?`3px solid ${GREEN}`:'3px solid transparent'}}>{label}</div>)}</div>
 </>;
};
