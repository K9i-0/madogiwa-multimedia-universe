const fs=require('fs'),path=require('path');
const {bundle}=require('@remotion/bundler');
const {renderStill,selectComposition,openBrowser}=require('@remotion/renderer');
(async()=>{
 const m=JSON.parse(fs.readFileSync('src/edit-manifest.json','utf8'));
 const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
 const browser=await openBrowser('chrome');
 const composition=await selectComposition({serveUrl,id:'H3Colab',puppeteerInstance:browser});
 const wanted=['bbq','hook_cost','title','colab','ai_plans','settings','h3_measure','seedance_cost','annual','annual_event','annual_limits','fair_cost','kling','h3_quality','license','ending'];
 for(const view of wanted){const d=m.dialogue.find(x=>x.view===view);await renderStill({serveUrl,composition,frame:d.startFrame+25,output:`out/preview-${view}.png`,imageFormat:'png',puppeteerInstance:browser});console.log(view);}
 await browser.close({silent:true});
})().catch(e=>{console.error(e);process.exit(1)});
