import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';import path from 'node:path';
const m=JSON.parse(fs.readFileSync('src/aura-hazard-wideui.json','utf8'));
fs.mkdirSync('out/hazard-wideui',{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/aura-hazard-wideui.tsx')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try{const composition=await selectComposition({serveUrl,id:'SobayaHazardWideUI',puppeteerInstance:browser});
if(process.argv.includes('--stills')){for(const frame of [150,190,210])await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,output:path.resolve(`out/hazard-wideui/frame-${frame}.jpg`),imageFormat:'jpeg'});}
else{let last=-1;await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:18,pixelFormat:'yuv420p',outputLocation:path.resolve('out/hazard-wideui/picture.mp4'),concurrency:4,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log(`${p*10}%`);}}});}
}finally{await browser.close({silent:true});}
if(!process.argv.includes('--stills'))execFileSync('ffmpeg',['-v','error','-y','-i','out/hazard-wideui/picture.mp4','-i','../final_remotion_sobaya_hazard_reference_9x16.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',path.resolve('..',m.output)],{stdio:'inherit'});
