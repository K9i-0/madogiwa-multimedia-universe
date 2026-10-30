import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const m=JSON.parse(fs.readFileSync('src/edit-manifest.json','utf8'));
const mode=process.argv[2]||'video';
const output=process.argv[3]||'../final_remotion_bbq_v3.mp4';
fs.mkdirSync('out',{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try{
 const composition=await selectComposition({serveUrl,id:'BBQ',puppeteerInstance:browser});
 if(mode==='stills'){
  for(const s of m.segments){
   const frame=s.startFrame+Math.min(s.durationInFrames-1,Math.round(s.durationInFrames*.5));
   await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,imageFormat:'png',output:`out/${s.id}.png`});console.log('STILL',s.id,frame);
  }
 }else{
  let last=-1;
  await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'png',concurrency:3,muted:true,outputLocation:'out/picture.mp4',onProgress:p=>{const pc=Math.floor(p.progress*100/10)*10;if(pc!==last){last=pc;console.log('RENDER',pc+'%');}}});
  execFileSync('ffmpeg',['-y','-v','error','-i','out/picture.mp4','-i','public/master.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',String(m.composition.durationInFrames/24),'-movflags','+faststart',output],{stdio:'inherit'});
 }
}finally{await browser.close({silent:true});}
