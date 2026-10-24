const {bundle}=require('@remotion/bundler');
const {renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
 const m=require('./src/edit-manifest.json');const out=path.resolve('out/stills');fs.mkdirSync(out,{recursive:true});
 const by=Object.fromEntries(m.narration.map(r=>[r.id,r]));
 const cases=[['title',52],['duo',by.n002.from+50],['warning',by.n006.from+30],['room',by.n012.from+30],['mask',by.n013.from+30],['broken',by.n022.from+20],['night',by.n029.from+30],['maskpress',by.n034.from+30],['home',by.n041.from+30],['blanket',by.n045.from+10],['cheek',by.n049.from+30],['phone',by.n055.from+30],['towel',by.n060.from+30],['F',by.n067.from+30],['mirror',by.n075.from+30],['maskrestored',by.n079.from+30],['ritual',by.n081.from+45],['closedeyes',by.n085.from+30],['pressure',by.n091.from+30],['falsevoice',by.n095.from+30],['turn',by.n100.from+30],['dawn',by.n107.from+10],['locked',by.n111.from+30],['end',by.n117.from+30]];
 const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});
 const browser=await openBrowser('chrome');
 try{
  const composition=await selectComposition({serveUrl,id:'YVillageMask',puppeteerInstance:browser});
  for(const [name,frame] of cases){await renderStill({serveUrl,composition,frame,output:path.join(out,name+'.png'),puppeteerInstance:browser,imageFormat:'png',logLevel:'error'});console.log(name,frame);}
 }finally{await browser.close({silent:true});}
 fs.writeFileSync('out/still-cases.json',JSON.stringify(cases,null,2));
})();
