const fs=require('fs'),path=require('path');
const {bundle}=require('@remotion/bundler');
const {renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
(async()=>{
 const m=JSON.parse(fs.readFileSync('src/edit-manifest.json','utf8'));
 const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
 const browser=await openBrowser('chrome');
 const composition=await selectComposition({serveUrl,id:'H3Colab',puppeteerInstance:browser});
 const output=`out/preview-${m.revision}`;fs.mkdirSync(output,{recursive:true});
 const frames=Object.fromEntries([...new Set(m.dialogue.map(x=>x.view))].map(view=>{const d=m.dialogue.find(x=>x.view===view);return [view,d.startFrame+25]}));
 for(const c of m.chapters.filter(x=>x.cardFrames>0))frames[`chapter-${c.number}`]=c.startFrame+30;
 for(const [view,frame] of Object.entries(frames)){await renderStill({serveUrl,composition,frame,output:`${output}/${view}.png`,imageFormat:'png',puppeteerInstance:browser});console.log(view);}
 await browser.close({silent:true});
})().catch(e=>{console.error(e);process.exit(1)});
