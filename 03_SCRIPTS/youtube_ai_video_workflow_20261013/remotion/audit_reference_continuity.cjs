// Inspect the exact frames omitted by mid-caption-only visual audits.
const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const fs=require('fs');
(async()=>{
 const m=require('./src/edit-manifest.json');
 const out='out/reference_continuity';fs.mkdirSync(out,{recursive:true});
 const points=[];
 for(const id of ['v001','v014','v042','v053','v064','v066','v070']){
  const d=m.dialogue.find(d=>d.id===id);
  for(const offset of [-1,0,1,8])points.push({group:id,name:`${id}_${offset}`,frame:d.startFrame+offset});
 }
 for(const id of ['v053','v064','v065','v069']){
  const d=m.dialogue.find(d=>d.id===id);
  for(const [i,s] of d.captionSegments.entries())if(i>0){
   for(const offset of [-1,0,1])points.push({group:`${id}_page${i}`,name:`${id}_page${i}_${offset}`,frame:d.startFrame+s.startFrame+offset});
  }
 }
 fs.writeFileSync(out+'/points.json',JSON.stringify(points,null,2));
 const serveUrl=await bundle({entryPoint:require('path').resolve('src/index.ts')});
 const browser=await openBrowser('chrome');
 try{
  const composition=await selectComposition({serveUrl,id:'Explainer',puppeteerInstance:browser});
  for(let i=0;i<points.length;i+=2){
   await Promise.all(points.slice(i,i+2).map(p=>renderStill({serveUrl,composition,frame:p.frame,output:out+'/'+p.name+'.png',puppeteerInstance:browser,logLevel:'error'})));
  }
 }finally{await browser.close({silent:true});}
 console.log(`Rendered ${points.length} boundary frames`);
})();
