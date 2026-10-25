const {bundle}=require('@remotion/bundler');
const {renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
 const m=JSON.parse(fs.readFileSync('src/edit-manifest.json'));
 const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
 const browser=await openBrowser('chrome');
 const composition=await selectComposition({serveUrl,id:'Explainer',puppeteerInstance:browser});
 fs.mkdirSync('out/previews',{recursive:true});
 const points=m.views.map((v,i)=>({frame:Math.min(v.startFrame+45,v.endFrame-1),view:v.view,index:i}));
 points.push({frame:m.codaStartFrame+90,view:'truth_factory',index:90},{frame:m.codaStartFrame+300,view:'truth_document',index:91});
 for(const p of points){await renderStill({serveUrl,composition,puppeteerInstance:browser,frame:p.frame,output:`out/previews/${String(p.index).padStart(2,'0')}_${p.view}.png`,logLevel:'error'});console.log(p.index,p.view);}
 fs.writeFileSync('out/previews/points.json',JSON.stringify(points,null,2));
 await browser.close({silent:true});
})();
