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
 const composition=await selectComposition({serveUrl,id:'AccidenchuaManners',puppeteerInstance:browser});
 if(mode==='stills'){
  const ids=process.argv.slice(3);
  const shots=m.segments.filter(s=>!['title'].includes(s.type)&&(!ids.length||ids.includes(s.id)));
  for(const s of shots){
   const chapter=m.chapters[(s.chapter||1)-1];
   if(s.type==='clip'&&!chapter.videoReady)continue;
   const offset=s.type==='opening'?100:Math.min(s.duration-1,s.type==='feedback'?Math.round(s.duration*.55):s.type==='ending'?s.duration-25:65);
   await renderStill({serveUrl,composition,puppeteerInstance:browser,frame:s.start+offset,imageFormat:'png',output:`out/${s.id}.png`});
   console.log('STILL',s.id);
  }
 }else{
  let last=-1;
  await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:17,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:96,concurrency:4,muted:true,outputLocation:'out/course-picture.mp4',onProgress:p=>{const pc=Math.floor(p.progress*100);if(pc!==last){last=pc;console.log('RENDER',pc+'%',p.renderedFrames);}}});
  execFileSync('ffmpeg',['-y','-v','error','-i','out/course-picture.mp4','-i','public/audio/master.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',String(m.composition.durationInFrames/24),'-movflags','+faststart','../'+(m.outputFile||'final_remotion_elearning.mp4')],{stdio:'inherit'});
 }
}finally{await browser.close({silent:true});}
