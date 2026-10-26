import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';import path from 'node:path';
const m=JSON.parse(fs.readFileSync('src/aura-cinematic.json','utf8'));
fs.mkdirSync('out/cinematic',{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/aura-cinematic.tsx')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try{const composition=await selectComposition({serveUrl,id:'CloneLabCinematic',puppeteerInstance:browser});
if(process.argv.includes('--stills')){for(const frame of [0,70,155,240,300,370,435,490,570,690,775,830,910,1008])await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,output:path.resolve(`out/cinematic/frame-${frame}.jpg`),imageFormat:'jpeg'});}
else{let last=-1;await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:18,pixelFormat:'yuv420p',outputLocation:path.resolve('out/cinematic/picture.mp4'),concurrency:4,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log(`${p*10}%`);}}});}
}finally{await browser.close({silent:true});}
if(!process.argv.includes('--stills'))execFileSync('ffmpeg',['-v','error','-y','-i','out/cinematic/picture.mp4','-i','public/aura/revenge.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-af','volume=0.56,afade=t=in:d=0.15,afade=t=out:st=34.35:d=0.65,alimiter=limit=0.84:level=false:latency=true','-c:a','aac','-b:a','192k','-t',String(m.composition.durationInFrames/m.composition.fps),'-movflags','+faststart',path.resolve('..',m.output)],{stdio:'inherit'});
