import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
const serveUrl=await bundle({entryPoint:path.resolve('src/h3-entry.tsx')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
try{
 const composition=await selectComposition({serveUrl,id:'YumemiGroupH3',puppeteerInstance:browser});
 if(process.argv[2]==='stills'){
  for(const frame of [0,24,72,180,300,324,360,372,396,444,540,612,684,714])await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,imageFormat:'png',output:`out/h3-${frame}.png`});
 }else{
  let last=-1;
  await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:18,pixelFormat:'yuv420p',imageFormat:'jpeg',jpegQuality:95,concurrency:3,outputLocation:'out/h3-render.mp4',onProgress:p=>{const pc=Math.floor(p.progress*100);if(pc!==last){last=pc;console.log('RENDER',pc+'%');}}});
  execFileSync('ffmpeg',['-v','error','-y','-i','out/h3-render.mp4','-i','public/shopping_irodori_instrumental_master_30s.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','30','-movflags','+faststart','../final_remotion_shopping_h3_768p.mp4'],{stdio:'inherit'});
 }
}finally{await browser.close({silent:true});}
