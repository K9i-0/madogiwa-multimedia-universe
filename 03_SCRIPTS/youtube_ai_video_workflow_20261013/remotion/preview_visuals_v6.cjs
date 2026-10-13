const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const fs=require('fs');
(async()=>{
 const m=require('./src/edit-manifest.json');
 const out='out/v6_stills';fs.mkdirSync(out,{recursive:true});
 const serveUrl=await bundle({entryPoint:require('path').resolve('src/index.ts')});
 const browser=await openBrowser('chrome');
 const composition=await selectComposition({serveUrl,id:'Explainer',puppeteerInstance:browser});
 let points=m.dialogue.map(d=>({name:d.id+'_'+d.view,frame:d.startFrame+Math.round(d.durationInFrames*.55)}));
 for(const id of ['u009','u012','u016','u024','u039','u044','u067','u069','u088','u090','u098']){
  const d=m.dialogue.find(d=>d.id===id);for(const t of [.1,.85])points.push({name:id+'_'+t,frame:d.startFrame+Math.round(d.durationInFrames*t)});
 }
 fs.writeFileSync(out+'/points.json',JSON.stringify(points));
 for(let i=0;i<points.length;i+=3){await Promise.all(points.slice(i,i+3).map(p=>renderStill({serveUrl,composition,frame:p.frame,output:out+'/'+p.name+'.png',puppeteerInstance:browser,logLevel:'error'})));console.log(i+'/'+points.length);}
 await browser.close({silent:true});
})();
