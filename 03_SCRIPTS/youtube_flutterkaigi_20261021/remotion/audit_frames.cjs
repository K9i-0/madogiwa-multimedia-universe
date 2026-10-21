const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
 const m=JSON.parse(fs.readFileSync('src/edit-manifest.json'));const views=new Map();
 for(const d of m.dialogue)if(!views.has(d.view))views.set(d.view,d.startFrame+Math.min(45,d.durationInFrames-1));
 fs.mkdirSync('out/audit',{recursive:true});const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});const browser=await openBrowser('chrome');
 const comp=await selectComposition({serveUrl,id:'FlutterKaigi',puppeteerInstance:browser});
 for(const [view,frame] of views){await renderStill({serveUrl,composition:comp,frame,output:`out/audit/${view}.png`,puppeteerInstance:browser});console.log(view,frame);}
 fs.writeFileSync('out/audit/frames.json',JSON.stringify([...views],null,2));await browser.close({silent:true});
})().catch(e=>{console.error(e);process.exit(1)});
