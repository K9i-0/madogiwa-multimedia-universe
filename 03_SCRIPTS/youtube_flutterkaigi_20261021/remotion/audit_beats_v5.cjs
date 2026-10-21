const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
 const m=JSON.parse(fs.readFileSync('src/edit-manifest.json'));const views=new Map();
 views.set('first_frame_v5',0);for(const d of m.dialogue){if(['title','stable','stack','widget_actions','deterministic','fps','memory','model_flow','game_odatetsu'].includes(d.view)){views.set(d.view+'_'+d.id+'_mid',d.startFrame+Math.floor(d.durationInFrames/2));views.set(d.view+'_'+d.id+'_end',d.startFrame+d.durationInFrames-1);}}
 fs.mkdirSync('out/beat_audit_v5',{recursive:true});const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});const browser=await openBrowser('chrome');
 const comp=await selectComposition({serveUrl,id:'FlutterKaigi',puppeteerInstance:browser});
 for(const [view,frame] of views){if(process.argv.includes("--workflow")&&!require("fs").readFileSync("src/WorkflowViews.tsx","utf8").includes("'"+view+"'"))continue;await renderStill({serveUrl,composition:comp,frame,output:`out/beat_audit_v5/${view}.png`,puppeteerInstance:browser});console.log(view,frame);}
 fs.writeFileSync('out/beat_audit_v5/frames.json',JSON.stringify([...views],null,2));await browser.close({silent:true});
})().catch(e=>{console.error(e);process.exit(1)});
