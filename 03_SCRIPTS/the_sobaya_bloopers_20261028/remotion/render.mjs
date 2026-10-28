import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const m=JSON.parse(fs.readFileSync('src/edit-manifest.json','utf8'));
if(m.pending.length)throw new Error('Missing inputs: '+m.pending.join(','));
fs.mkdirSync('out',{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.tsx')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try{
 const composition=await selectComposition({serveUrl,id:m.composition.id,puppeteerInstance:browser});
 if(process.argv.includes('--stills')){
  for(const s of m.segments)await renderStill({serveUrl,composition,puppeteerInstance:browser,frame:s.start+Math.min(s.duration-1,45),output:`out/${s.id}.png`});
 }else{
  let last=-1;
  await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:17,pixelFormat:'yuv420p',concurrency:3,muted:true,outputLocation:'out/picture_v1.mp4',onProgress:p=>{const pc=Math.floor(p.progress*20)*5;if(pc!==last){last=pc;console.log('RENDER',pc+'%');}}});
  const dur=m.composition.durationInFrames/m.composition.fps;
  execFileSync('ffmpeg',['-y','-v','error','-i','out/picture_v1.mp4','-i','public/master.mp4','-map','0:v:0','-map','1:a:0','-c:v','copy','-af',`afade=t=out:st=${dur-0.32}:d=0.32,alimiter=limit=0.95:level=false`,'-c:a','aac','-b:a','192k','-ar','48000','-t',String(dur),'-movflags','+faststart','../final_remotion_bloopers_v1.mp4'],{stdio:'inherit'});
  console.log('READY',path.resolve('../final_remotion_bloopers_v1.mp4'));
 }
}finally{await browser.close({silent:true});}
