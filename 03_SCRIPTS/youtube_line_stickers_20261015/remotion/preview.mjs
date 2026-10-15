import {bundle} from '@remotion/bundler';
import {renderStill,openBrowser} from '@remotion/renderer';
import fs from 'node:fs';

// Render one measured frame per view; --layout allows inspection before voice timing.
const layout=process.argv.includes('--layout');
const manifest=JSON.parse(fs.readFileSync('src/edit-manifest.json'));
const lines=JSON.parse(fs.readFileSync('dialogue.json'));
const chosen=new Map();
const captionWeight=d=>Math.max(0,...(d.captionSegments??[{text:d.caption??d.text}]).map(s=>s.text.replace(/\n/g,'').length));
for(const d of (layout?lines:manifest.dialogue)){if(!chosen.has(d.view)||(!layout&&captionWeight(d)>captionWeight(chosen.get(d.view))))chosen.set(d.view,d);}
fs.mkdirSync('out',{recursive:true});
const serveUrl=await bundle({entryPoint:'src/index.ts',publicDir:'public'});
const browser=await openBrowser('chrome');
try {
 const entries=[...chosen.entries()];
 for(let i=0;i<entries.length;i+=3)await Promise.all(entries.slice(i,i+3).map(async([view,d])=>{
  const row=layout?{...d,startFrame:0,durationInFrames:300,caption:d.text.slice(0,23)+'\n'+d.text.slice(23,46),envelope:Array(300).fill(.5)}:d;
  const inputProps=layout?{silentPreview:true,manifest:{composition:{width:1280,height:720,fps:30,durationInFrames:900},dialogue:[row]}}:{silentPreview:true};
  const longest=(row.captionSegments??[]).reduce((max,s)=>s.text.length>(max?.text.length??-1)?s:max,undefined);
  const frame=layout?45:row.startFrame+(longest?Math.floor((longest.startFrame+longest.endFrame)/2):Math.min(45,row.durationInFrames-1));
  await renderStill({serveUrl,composition:{id:'Explainer',width:1280,height:720,fps:30,durationInFrames:layout?900:manifest.composition.durationInFrames,props:inputProps,defaultProps:{}},inputProps,output:`out/${layout?'preview':'audit'}-${view}.png`,frame,puppeteerInstance:browser,logLevel:'error'});
  console.log(`${view}: ${frame}`);
 }));
}finally{await browser.close({silent:true});}
