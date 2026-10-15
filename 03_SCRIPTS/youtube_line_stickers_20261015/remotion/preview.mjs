import {bundle} from '@remotion/bundler';
import {renderStill,openBrowser} from '@remotion/renderer';
import fs from 'node:fs';

// Default: the longest subtitle page of each view, using the measured timeline.
// --layout works before voice timing. --view=roles --all-pages audits each page.
const layout=process.argv.includes('--layout');
const allPages=process.argv.includes('--all-pages');
const allUtterances=process.argv.includes('--all-utterances');
const ids=process.argv.find(x=>x.startsWith('--ids='))?.slice(6).split(',');
const fractions=process.argv.find(x=>x.startsWith('--fractions='))?.slice(12).split(',').map(Number);
const viewFilter=process.argv.find(x=>x.startsWith('--view='))?.slice(7);
const prefix=process.argv.find(x=>x.startsWith('--prefix='))?.slice(9)??(layout?'preview':'audit');
const manifest=JSON.parse(fs.readFileSync('src/edit-manifest.json'));
const lines=JSON.parse(fs.readFileSync('dialogue.json'));
const candidates=(layout?lines:manifest.dialogue).filter(d=>(!viewFilter||d.view===viewFilter)&&(!ids||ids.includes(d.id)));
const captionWeight=d=>Math.max(0,...(d.captionSegments??[{text:d.caption??d.text}]).map(s=>s.text.replace(/\n/g,'').length));
const chosen=new Map();
for(const d of candidates){if(!chosen.has(d.view)||(!layout&&captionWeight(d)>captionWeight(chosen.get(d.view))))chosen.set(d.view,d);}
const shots=[];
for(const d of allPages||allUtterances||ids?candidates:chosen.values()){
 const row=layout?{...d,startFrame:0,durationInFrames:300,caption:d.text.slice(0,23)+'\n'+d.text.slice(23,46),envelope:Array(300).fill(.5)}:d;
 const longest=(row.captionSegments??[]).reduce((max,s)=>s.text.length>(max?.text.length??-1)?s:max,undefined);
 const pages=fractions?fractions.map(f=>({startFrame:Math.floor(row.durationInFrames*f),endFrame:Math.floor(row.durationInFrames*f)})):allPages?(row.captionSegments??[undefined]):[longest];
 pages.forEach((segment,i)=>shots.push({
  name:allPages||allUtterances||ids||fractions?`${row.view}-${row.id}-${i+1}`:row.view,
  frame:row.startFrame+(segment?Math.floor((segment.startFrame+segment.endFrame)/2):Math.min(45,row.durationInFrames-1)),
  inputProps:layout?{silentPreview:true,manifest:{composition:{width:1280,height:720,fps:30,durationInFrames:900},dialogue:[row]}}:{silentPreview:true},
 }));
}
fs.mkdirSync('out',{recursive:true});
const serveUrl=await bundle({entryPoint:'src/index.ts',publicDir:'public'});
const browser=await openBrowser('chrome');
try {
 for(let i=0;i<shots.length;i+=3)await Promise.all(shots.slice(i,i+3).map(async({name,frame,inputProps})=>{
  await renderStill({serveUrl,composition:{id:'Explainer',width:1280,height:720,fps:30,durationInFrames:layout?900:manifest.composition.durationInFrames,props:inputProps,defaultProps:{}},inputProps,output:`out/${prefix}-${name}.png`,frame,puppeteerInstance:browser,logLevel:'error'});
  console.log(`${name}: ${frame}`);
 }));
}finally{await browser.close({silent:true});}
fs.writeFileSync(`out/${prefix}-frames.json`,JSON.stringify(shots.map(({name,frame})=>({name,frame})),null,2));
