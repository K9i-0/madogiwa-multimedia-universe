const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
 const m=JSON.parse(fs.readFileSync('src/edit-manifest.json'));const views=new Map();
 for(const d of m.dialogue)if((d.view.startsWith('v11_')||['scene','v9_scene_layer','stable','model_flow','tripo','mcp_overview','fps','memory','gallery_model','gallery_stage','widget_actions','game_odatetsu','v10_inside'].includes(d.view))&&!views.has(d.view+':'+(m.dialogue.filter(x=>x.view===d.view&&x.startFrame<=d.startFrame).length)))views.set(d.view+':'+(m.dialogue.filter(x=>x.view===d.view&&x.startFrame<=d.startFrame).length),d.startFrame+Math.min(45,d.durationInFrames-1));
 fs.mkdirSync('out/audit_v11',{recursive:true});const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});const browser=await openBrowser('chrome');
 const comp=await selectComposition({serveUrl,id:'FlutterKaigi',puppeteerInstance:browser});
 for(const [view,frame] of views){await renderStill({serveUrl,composition:comp,frame,output:`out/audit_v11/${view.replace(':','_')}.png`,puppeteerInstance:browser});console.log(view,frame);}
 fs.writeFileSync('out/audit_v11/frames.json',JSON.stringify([...views],null,2));await browser.close({silent:true});
})().catch(e=>{console.error(e);process.exit(1)});
