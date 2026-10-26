import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
const m=JSON.parse(fs.readFileSync('src/edit-manifest-h3.json','utf8'));
const serveUrl=await bundle({entryPoint:path.resolve('src/h3-entry.tsx')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try{
 const composition=await selectComposition({serveUrl,id:'MadogiwaKeynoteH3',puppeteerInstance:browser});
 if(process.argv[2]==='stills'){
  for(const line of m.lines){
   await renderStill({serveUrl,composition,puppeteerInstance:browser,frame:Math.min(line.end-1,line.start+18),imageFormat:'png',output:`out/h3-${line.id}.png`});
  }
 }else{
  let last=-1;
  await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:18,pixelFormat:'yuv420p',audioBitrate:'192k',imageFormat:'jpeg',jpegQuality:95,concurrency:3,outputLocation:'out/h3-render.mp4',onProgress:p=>{const pc=Math.floor(p.progress*100);if(pc!==last){last=pc;console.log('RENDER',pc+'%',p.renderedFrames,'frames');}}});
  // Mux original PCM directly to avoid Remotion audio encoder's 2048-sample delay.
  execFileSync('ffmpeg',['-y','-v','error','-i','out/h3-render.mp4','-i','public/'+m.audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t',String(m.durationInFrames/m.fps),'-movflags','+faststart','../final_remotion_h3_irodori.mp4'],{stdio:'inherit'});
 }
}finally{await browser.close({silent:true});}
