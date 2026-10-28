import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const m=JSON.parse(fs.readFileSync('src/edit-manifest.json','utf8'));
const mode=process.argv[2]||'video';
if(mode==='video'&&m.pending.length)throw new Error('Missing production inputs: '+m.pending.join(', '));
fs.mkdirSync('out',{recursive:true});
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try{
 const composition=await selectComposition({serveUrl,id:'MegaMugDVD',puppeteerInstance:browser});
 if(mode==='stills'){
  for(const s of m.segments){
   if((s.type==='scene'||s.id==='explain01')&&m.pending.includes('H3'))continue;
   const frame=s.start+Math.min(s.duration-1,s.type==='opening'?65:Math.round(s.duration*.55));
   await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,imageFormat:'png',output:`out/${s.id}.png`});console.log('STILL',s.id,frame);
  }
 }else{
  let last=-1;
  await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:16,pixelFormat:'yuv420p',imageFormat:'png',concurrency:3,muted:true,outputLocation:'out/picture.mp4',onProgress:p=>{const pc=Math.floor(p.progress*100/5)*5;if(pc!==last){last=pc;console.log('RENDER',pc+'%');}}});
  execFileSync('ffmpeg',['-y','-v','error','-i','out/picture.mp4','-i','public/master.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',String(m.composition.durationInFrames/m.composition.fps),'-movflags','+faststart','../final_remotion_mega_dvd.mp4'],{stdio:'inherit'});
 }
}finally{await browser.close({silent:true});}
