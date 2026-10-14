// Render the three requested Shorts; horizontal sources are read-only.
import {bundle} from '@remotion/bundler';
import {renderMedia,selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const repo=path.resolve('../../..'),episodes=['80_sobaya_clone_lab','85_pakurareta','84_madogiwa_tribe_origin'];
for(const ep of episodes){const m=JSON.parse(fs.readFileSync(path.join(repo,'03_SCRIPTS',ep,'shorts-manifest-usagi.json')));for(const c of m.clips){const dst=path.resolve('public',c.file);if(!fs.existsSync(dst))fs.linkSync(path.join(repo,c.source),dst);}}
const url=await bundle({entryPoint:path.resolve('src/index.tsx'),publicDir:path.resolve('public')});
for(const ep of episodes){
 const dir=path.join(repo,'03_SCRIPTS',ep),m=JSON.parse(fs.readFileSync(path.join(dir,'shorts-manifest-usagi.json'))),composition=await selectComposition({serveUrl:url,id:'Shorts',inputProps:m});
 const silent=path.join(dir,'remotion/out/shorts-usagi/silent.mp4');console.log('START',ep);let milestone=0;
 await renderMedia({serveUrl:url,composition,inputProps:m,outputLocation:silent,codec:'h264',crf:18,concurrency:2,muted:true,logLevel:'error',onProgress:({progress})=>{const n=Math.floor(progress*4);if(n>milestone){milestone=n;console.log(ep,n*25+'%');}}});
 execFileSync('ffmpeg',['-v','error','-y','-i',silent,'-i',path.join(repo,m.audioSource),'-map','0:v:0','-map','1:a:0','-c','copy','-t',String(m.durationInFrames/m.fps),'-movflags','+faststart',path.join(dir,'final_remotion_shorts_usagi_9x16.mp4')]);console.log('DONE',ep);
}
