const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,openBrowser}=require('@remotion/renderer');
const fs=require('fs'),path=require('path');
(async()=>{
 const m=JSON.parse(fs.readFileSync('src/edit-manifest.json'));const views=new Map();
 for(const d of m.dialogue)if((['v9_timeline','v14_contrib','v15_article'].includes(d.view))&&!views.has(d.view))views.set(d.view,d.startFrame+Math.min(45,d.durationInFrames-1));
 const ds=m.dialogue.filter(d=>d.view==='v14_contrib');views.set('contrib_history',ds[3].startFrame+90);
 fs.mkdirSync('out/audit_v15',{recursive:true});const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public')});const browser=await openBrowser('chrome');
 const comp=await selectComposition({serveUrl,id:'FlutterKaigi',puppeteerInstance:browser});
 for(const [view,frame] of views){if(process.argv.includes("--workflow")&&!require("fs").readFileSync("src/WorkflowViews.tsx","utf8").includes("'"+view+"'"))continue;await renderStill({serveUrl,composition:comp,frame,output:`out/audit_v15/${view}.png`,puppeteerInstance:browser});console.log(view,frame);}
 fs.writeFileSync('out/audit_v15/frames.json',JSON.stringify([...views],null,2));await browser.close({silent:true});
})().catch(e=>{console.error(e);process.exit(1)});
