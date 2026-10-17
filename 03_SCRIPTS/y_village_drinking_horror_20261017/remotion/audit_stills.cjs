const {bundle}=require('@remotion/bundler');
const {renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
 const m=require('./src/edit-manifest.json');const out=path.resolve('out/stills-v6');fs.mkdirSync(out,{recursive:true});
 const by=Object.fromEntries(m.narration.map(r=>[r.id,r]));
 const cases=[['title',45],['excel','n0002v5a1'],['m','n0004'],['y','n0006'],['village','n0019'],['warning','n0027'],['monkeys','n0048a'],['bowl','n0053'],['blame','n0085v5r2'],['cans','n0109'],['recording','n0134'],['cold-answer','n0143'],['empty-room','n0192'],['applause-wait','n0202'],['silhouette','n0214'],['awareness','n0219v6a4'],['costume','n0228'],['aura','n0255v5a3'],['authority','n0238'],['rule','n0265'],['four-mugs','n0297'],['before-reveal',m.revealFrame-1],['reveal',m.revealFrame+30],['skin','n0320'],['cup','n0333'],['f-view','n0346'],['applause','n0367'],['escape','n0375'],['request','n0415'],['empty-mug','n0421'],['asleep','n0427'],['morning','n0460'],['return','n0471v6a0'],['ending','n0486']];
 const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
 const browser=await openBrowser('chrome');
 try{
  const composition=await selectComposition({serveUrl,id:'YVillage',puppeteerInstance:browser});
  for(const [name,anchor] of cases){const frame=typeof anchor==='number'?anchor:by[anchor].from+Math.min(30,Math.floor(by[anchor].duration/2));
   await renderStill({serveUrl,composition,frame,output:path.join(out,name+'.png'),puppeteerInstance:browser,imageFormat:'png',logLevel:'error'});
   console.log(name,frame);
  }
 }finally{await browser.close({silent:true});}
})();
