import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill} from '@remotion/renderer';
import fs from 'node:fs';
const m=JSON.parse(fs.readFileSync('src/edit-manifest.json','utf8'));
const url=await bundle({entryPoint:'src/index.ts'});
const composition=await selectComposition({serveUrl:url,id:'Explainer'});
const frames=[];let last='';
for(const d of m.dialogue){if(last!==d.view){frames.push({view:d.view,frame:d.startFrame+Math.min(45,d.durationInFrames-1)});last=d.view;}}
frames.push({view:'credits',frame:m.creditsStartFrame+30});
const selected=process.argv.slice(2);if(selected.length){for(let i=frames.length-1;i>=0;i--){if(!selected.includes(frames[i].view))frames.splice(i,1);}}
for(let i=0;i<frames.length;i+=3){await Promise.all(frames.slice(i,i+3).map(async ({view,frame})=>{await renderStill({serveUrl:url,composition,output:`out/qa_${view}_${frame}.png`,frame,logLevel:'error'});console.log(view,frame);}));}
fs.writeFileSync('out/preview_frames.json',JSON.stringify(frames,null,2));
