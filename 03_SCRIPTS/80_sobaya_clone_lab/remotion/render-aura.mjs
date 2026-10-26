import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
const serveUrl=await bundle({entryPoint:path.resolve('src/aura.tsx')});
const browser=await openBrowser('chrome',{browserExecutable:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
fs.mkdirSync('out/aura-prep',{recursive:true});
try{
 const composition=await selectComposition({serveUrl,id:'CloneLabAuraShort',puppeteerInstance:browser});
 if(process.argv.includes('--stills')){
 for(const frame of [40,170,240,380,457,490,570,620,660]) await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,output:path.resolve(`out/aura-prep/frame-${frame}.jpg`),imageFormat:'jpeg'});
 }else await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',crf:18,pixelFormat:'yuv420p',outputLocation:path.resolve('out/aura-prep/picture.mp4'),concurrency:4,onProgress:({progress})=>{if(Math.round(progress*100)%20===0)process.stdout.write(`${Math.round(progress*100)}% `);}});
}finally{await browser.close({silent:true});}
