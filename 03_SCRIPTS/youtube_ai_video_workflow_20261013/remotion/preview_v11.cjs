const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const fs=require('fs');
(async()=>{
 const m=require('./src/edit-manifest.json');
 const out='out/v11_stills';fs.mkdirSync(out,{recursive:true});
 const serveUrl=await bundle({entryPoint:require('path').resolve('src/index.ts')});
 const browser=await openBrowser('chrome');
 const composition=await selectComposition({serveUrl,id:'Explainer',puppeteerInstance:browser});
 let points=[{name:'opening',frame:30}];
 for(const d of m.dialogue){
  for(const [i,s] of (d.captionSegments??[{startFrame:0,endFrame:d.durationInFrames}]).entries())points.push({name:d.id+'_caption'+i,frame:d.startFrame+s.startFrame+Math.min(24,Math.floor((s.endFrame-s.startFrame)/2))});
 }
 const cues=require('./src/visual-cues-v11.json');
 for(const [id,line] of Object.entries(cues)){
  const d=m.dialogue.find(d=>d.id===id);for(const [i,t] of Object.values(line).entries())points.push({name:id+'_cue'+i,frame:d.startFrame+t+10});
 }
 const selected=process.argv.slice(2);if(selected.length)points=points.filter(p=>selected.some(id=>p.name.startsWith(id)));
 fs.writeFileSync(out+(selected.length?'/points_selected.json':'/points.json'),JSON.stringify(points));
 for(let i=0;i<points.length;i+=4){await Promise.all(points.slice(i,i+4).map(p=>renderStill({serveUrl,composition,frame:p.frame,output:out+'/'+p.name+'.png',puppeteerInstance:browser,logLevel:'error'})));console.log(i+'/'+points.length);}
 await browser.close({silent:true});
})();
