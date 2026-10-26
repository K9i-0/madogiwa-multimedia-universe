import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';import path from 'node:path';
const m=JSON.parse(fs.readFileSync('src/aura-hazard-reference.json','utf8'));
fs.mkdirSync('out/hazard-reference',{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/aura-hazard-reference.tsx')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try{const composition=await selectComposition({serveUrl,id:'SobayaHazardReference',puppeteerInstance:browser});
if(process.argv.includes('--stills')){for(const frame of [0,30,55,81,150,190,240,360,387,388,400,460,525,570,620])await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,output:path.resolve(`out/hazard-reference/frame-${frame}.jpg`),imageFormat:'jpeg'});}
else{let last=-1;await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:18,pixelFormat:'yuv420p',outputLocation:path.resolve('out/hazard-reference/picture.mp4'),concurrency:4,onProgress:({progress})=>{const p=Math.floor(progress*10);if(p!==last){last=p;console.log(`${p*10}%`);}}});}
}finally{await browser.close({silent:true});}
if(!process.argv.includes('--stills'))execFileSync('ffmpeg',['-v','error','-y','-i','out/hazard-reference/picture.mp4','-i','public/aura/revenge.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-af',`atrim=start=${m.music.startSample/m.music.sampleRate}:duration=${m.composition.durationInFrames/m.composition.fps},asetpts=PTS-STARTPTS,volume=0.48,afade=t=in:d=0.04,afade=t=out:st=${m.music.fadeOutStartFrame/m.composition.fps}:d=${m.music.fadeOutDurationFrames/m.composition.fps},alimiter=limit=0.8:level=false:latency=true`,'-c:a','aac','-b:a','192k','-t',String(m.composition.durationInFrames/m.composition.fps),'-movflags','+faststart',path.resolve('..',m.output)],{stdio:'inherit'});
