const {bundle}=require('@remotion/bundler');
const {renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
const m=require('./src/edit-manifest.json');const out=path.resolve('out/stills-v5');fs.mkdirSync(out,{recursive:true});
const by=Object.fromEntries(m.narration.map(r=>[r.id,r]));
const cases=[['title',45],['excel','n0002v5a1'],['bad-ui','n0004v5a1'],['password','n0006v5a1'],['bug-report','n0007v5a2'],['monkeys','n0048a'],['blame','n0085v5r2'],['report','n0096av5a1'],['recording','n0145'],['drink-record','n0162v5a1'],['silhouette','n0214'],['costume','n0228'],['aura','n0255v5a3'],['rule','n0265'],['invitation','n0272v5r2'],['reveal',m.revealFrame+30],['skin','n0320'],['cup','n0333'],['f-view','n0346'],['escape','n0371v5r1'],['asleep','n0427'],['morning','n0460'],['return','n0471v5a2'],['ending','n0486']];
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
const browser=await openBrowser('chrome');
try{
const composition=await selectComposition({serveUrl,id:'YVillage',puppeteerInstance:browser});
for(const [name,anchor] of cases){const frame=typeof anchor==='number'?anchor:by[anchor].from+Math.min(36,by[anchor].duration-1);
 await renderStill({serveUrl,composition,frame,output:path.join(out,name+'.png'),puppeteerInstance:browser,imageFormat:'png',logLevel:'error'});
 console.log(name,frame);
}
}finally{await browser.close({silent:true});}
})();
