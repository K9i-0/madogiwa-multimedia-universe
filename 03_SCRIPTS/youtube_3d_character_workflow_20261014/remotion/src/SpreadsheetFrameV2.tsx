import React from 'react';
const GREEN='#176B47';const tabs=['完成例','回転動画','Tripoで生成','料金と選び方','手直し','骨と動作','活用','まとめ'];
export function SpreadsheetFrameV2({chapter,progress,children}:{chapter:string;progress:number;children:React.ReactNode}){
 const section=Math.max(0,Number(chapter.split('.')[0])-1);
 return <><div style={{position:'absolute',inset:0,background:'#fff'}}/>
 <div style={{position:'absolute',left:30,right:0,top:76,bottom:31,backgroundImage:'linear-gradient(to right,#edf0ee 1px,transparent 1px),linear-gradient(to bottom,#edf0ee 1px,transparent 1px)',backgroundSize:'156px 59px'}}/>
 <div style={{position:'absolute',left:0,right:0,top:0,height:30,background:GREEN,color:'#fff',display:'flex',alignItems:'center',padding:'0 18px',fontSize:17,fontWeight:600}}>窓際族物語<span style={{opacity:.4,margin:'0 13px'}}>/</span>画像から、動く3Dへ<span style={{marginLeft:'auto',fontSize:13,fontWeight:400}}>やめ太郎 ＆ たこさん</span></div>
 <div style={{position:'absolute',left:0,right:0,top:30,height:25,background:'#f6f8f6',borderBottom:'1px solid #cbd4ce',display:'flex',alignItems:'center',fontSize:16}}><div style={{width:100,textAlign:'center',borderRight:'1px solid #c9d1cc',color:'#647168'}}>B2:H9</div><div style={{width:40,textAlign:'center',fontFamily:'Georgia',fontStyle:'italic',color:'#6b7770'}}>fx</div><div>{chapter}</div></div>
 <div style={{position:'absolute',left:30,right:0,top:55,height:21,display:'flex',background:'#edf1ee',borderBottom:'1px solid #cbd4ce'}}>{'ABCDEFGH'.split('').map(c=><div key={c} style={{flex:1,textAlign:'center',fontSize:12,color:'#6b786f',borderRight:'1px solid #d1dad4'}}>{c}</div>)}</div>
 <div style={{position:'absolute',left:0,top:76,bottom:31,width:30,background:'#edf1ee',borderRight:'1px solid #cbd4ce'}}>{Array.from({length:11},(_,i)=><div key={i} style={{height:59,textAlign:'center',paddingTop:19,boxSizing:'border-box',fontSize:12,color:'#6b786f'}}>{i+1}</div>)}</div>
 {children}
 <div style={{position:'absolute',left:0,right:0,bottom:0,height:31,background:'#f0f3f1',borderTop:'1px solid #bccbc1',display:'flex',paddingLeft:30}}>{tabs.map((s,i)=><div key={s} style={{position:'relative',fontSize:14,padding:'5px 18px',background:section===i?'#fff':'transparent',color:section===i?GREEN:'#647168',fontWeight:section===i?700:400,borderRight:'1px solid #d6dfd9'}}>{s}{section===i&&<div style={{position:'absolute',bottom:0,left:0,height:3,width:`${Math.max(4,progress*100)}%`,background:GREEN}}/>}</div>)}</div>
 </>;
}
