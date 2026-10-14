import {bundle} from '@remotion/bundler';
import {renderMedia,selectComposition,renderStill} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
const root=path.resolve('..'),repo=path.resolve('../../..');
const queue=JSON.parse(fs.readFileSync(path.join(root,'queue.json'),'utf8'));
const selected=process.argv.slice(2).filter(x=>!x.startsWith('--'));
const still=process.argv.includes('--still');
for(const slug of selected) if(!queue.some(r=>r.slug===slug)) throw new Error('Unknown slug: '+slug);
const url=await bundle({entryPoint:path.resolve('src/index.tsx'),publicDir:path.resolve('public')});
for(const row of queue.filter(r=>!selected.length||selected.includes(r.slug))){
 const manifestRaw=fs.readFileSync(path.join(repo,row.manifest),'utf8');
 const m=JSON.parse(manifestRaw);
 console.log(still?'STILL':'START',row.slug);
 const composition=await selectComposition({serveUrl:url,id:'Shorts',inputProps:m});
 fs.mkdirSync(path.resolve('out'),{recursive:true});
 if(still){await renderStill({serveUrl:url,composition,inputProps:m,output:path.resolve('out',row.slug+'.png'),frame:m.captions[0]?.startFrame+5||3});continue;}
 const output=path.join(repo,row.output),silent=path.resolve('out',row.slug+'.mp4');
 let milestone=0;
 await renderMedia({onProgress:({progress})=>{const next=Math.floor(progress*4);if(next>milestone){milestone=next;console.log(row.slug,next*25+'%');}},serveUrl:url,composition,inputProps:m,outputLocation:silent,codec:'h264',crf:18,concurrency:2,muted:true,logLevel:'error'});
 execFileSync('ffmpeg',['-v','error','-i',silent,'-i',path.join(repo,m.audioSource??row.source),'-map','0:v:0','-map','1:a:0','-c','copy',...(m.audioTrimEndFrame ? ['-t',String(m.audioTrimEndFrame/m.fps)] : []),'-movflags','+faststart','-y',output]);
 fs.writeFileSync(path.resolve('out',row.slug+'.render.json'),JSON.stringify({output:row.output,manifestSha256:crypto.createHash('sha256').update(manifestRaw).digest('hex'),sha256:crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex'),renderedAt:new Date().toISOString()},null,2));
 console.log('DONE',row.slug);
}
