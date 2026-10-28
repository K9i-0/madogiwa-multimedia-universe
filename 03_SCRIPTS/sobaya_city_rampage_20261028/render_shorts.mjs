import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
const base=path.dirname(fileURLToPath(import.meta.url));
const shared=path.resolve(base,'../shorts_queue_20261011/remotion');
const require=createRequire(path.join(shared,'package.json'));
const {bundle}=require('@remotion/bundler');
const {selectComposition,renderMedia,renderStill}=require('@remotion/renderer');
const manifest=JSON.parse(fs.readFileSync(path.join(base,'shorts-manifest.json'),'utf8'));
const work=path.join(base,'generated/shorts'),pub=path.join(work,'public');
fs.mkdirSync(pub,{recursive:true});
const source=path.join(base,manifest.audioSource),input=path.join(pub,'input.mp4');
if(!fs.existsSync(input))fs.linkSync(source,input);
const serveUrl=await bundle({entryPoint:path.join(shared,'src/index.tsx'),publicDir:pub});
const composition=await selectComposition({serveUrl,id:'Shorts',inputProps:manifest});
if(process.argv.includes('--still')){
 await renderStill({serveUrl,composition,inputProps:manifest,frame:60,output:path.join(work,'preview.png')});
 console.log('STILL: '+path.join(work,'preview.png'));
}else{
 const silent=path.join(work,'silent.mp4');let last=0;
 await renderMedia({serveUrl,composition,inputProps:manifest,outputLocation:silent,codec:'h264',crf:18,concurrency:2,muted:true,logLevel:'error',onProgress:({progress})=>{let n=Math.floor(progress*4);if(n>last){last=n;console.log(n*25+'%');}}});
 const output=path.join(base,'final_remotion_shorts_9x16.mp4');
 execFileSync('ffmpeg',['-v','error','-i',silent,'-i',source,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-y',output]);
 console.log('READY: '+output);
}
