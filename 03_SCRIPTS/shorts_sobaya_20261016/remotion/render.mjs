// Static React title/caption cards, composited over synchronized original footage.
// Usage: node render.mjs <repo-relative manifest.json> [--cards-only]
import {bundle} from '@remotion/bundler';
import {openBrowser,renderStill,selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../..');
const manifest=path.resolve(repo,process.argv[2]);
const m=JSON.parse(fs.readFileSync(manifest,'utf8'));
const dir=path.join(here,'out',m.slug);fs.mkdirSync(dir,{recursive:true});
const url=await bundle({entryPoint:path.join(here,'src/index.tsx')});
const browser=await openBrowser('chrome');
const comp=await selectComposition({serveUrl:url,id:'Overlay',inputProps:m,puppeteerInstance:browser});
const boundaries=[...new Set([0,m.durationInFrames,...m.captions.flatMap(c=>[c.startFrame,c.endFrame]),...(m.titleCues??[]).map(c=>c.from),...(m.credits??[]).flatMap(c=>[c.from,c.to])])].filter(x=>x>=0&&x<=m.durationInFrames).sort((a,b)=>a-b);
const cards=[];
try{
 for(let i=0;i<boundaries.length-1;i++){
  const frame=boundaries[i],file=path.join(dir,`card-${String(i).padStart(3,'0')}.png`);
  await renderStill({serveUrl:url,composition:comp,inputProps:m,output:file,frame,imageFormat:'png',logLevel:'error',puppeteerInstance:browser});
  cards.push({from:frame,to:boundaries[i+1],file});
 }
}finally{await browser.close({silent:true});}
fs.writeFileSync(path.join(dir,'cards.json'),JSON.stringify(cards,null,2));
if(process.argv.includes('--cards-only'))process.exit(0);
const quote=s=>s.replaceAll("'","'\\''");
fs.writeFileSync(path.join(dir,'cards.ffconcat'),'ffconcat version 1.0\n'+cards.map(c=>`file '${quote(c.file)}'\noption framerate ${m.fps}\nduration ${(c.to-c.from)/m.fps}\n`).join('')+`file '${quote(cards.at(-1).file)}'\noption framerate ${m.fps}\n`);
const source=path.resolve(repo,m.source),audio=path.resolve(repo,m.audioSource??m.source),output=path.resolve(repo,m.output??path.relative(repo,path.join(path.dirname(manifest),'final_remotion_shorts_9x16.mp4')));
const crop=m.crop?`crop=${m.crop.width}:${m.crop.height}:${m.crop.x}:${m.crop.y},`:'';
const start=m.trimStartFrame??0;
const filter=`[0:v]trim=start_frame=${start}:end_frame=${start+m.durationInFrames},setpts=PTS-STARTPTS,${crop}split=2[bgsrc][fgsrc];[bgsrc]scale=204:362:force_original_aspect_ratio=increase,crop=180:320,gblur=sigma=8.5:steps=2,lutrgb=r='val*0.47+17*0.53':g='val*0.47+24*0.53':b='val*0.47+32*0.53',scale=720:1280:flags=bilinear[bg];[1:v]fps=${m.fps},format=rgba[txt];[bg][txt]overlay=0:0:format=auto[base];[fgsrc]scale=720:480:force_original_aspect_ratio=decrease:flags=lanczos[fg];[base][fg]overlay=x=(W-w)/2:y=350+(480-h)/2:format=auto,format=yuv420p[out]`;
const silent=path.join(dir,'silent.mp4');
const encoder=m.encoder??process.env.MMU_SHORTS_ENCODER??(process.platform==='darwin'?'h264_videotoolbox':'libx264');
const encodeArgs=encoder==='h264_videotoolbox'?['-c:v',encoder,'-q:v','75','-allow_sw','0','-profile:v','high']:['-c:v','libx264','-preset','veryfast','-crf','18','-threads','2'];
execFileSync('ffmpeg',['-hide_banner','-loglevel','error','-threads','2','-reinit_filter','0','-i',source,'-f','concat','-safe','0','-threads','2','-i',path.join(dir,'cards.ffconcat'),'-filter_complex_threads','2','-filter_complex',filter,'-map','[out]','-an','-frames:v',String(m.durationInFrames),'-r',String(m.fps),...encodeArgs,'-y',silent],{stdio:'inherit'});
// Do not accept a video whose final card or scene was lost to decoder metadata changes.
const rendered=JSON.parse(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',silent],{encoding:'utf8'}));
if(Number(rendered.streams[0].nb_frames)!==m.durationInFrames)throw new Error(`Frame mismatch for ${m.slug}: ${rendered.streams[0].nb_frames} != ${m.durationInFrames}`);
const args=['-hide_banner','-loglevel','error','-i',silent];
if(start)args.push('-ss',String(start/m.fps));
args.push('-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy');
if(m.trimAudio)args.push('-t',String(m.durationInFrames/m.fps));
args.push('-movflags','+faststart','-y',output);
execFileSync('ffmpeg',args,{stdio:'inherit'});
console.log('DONE',m.slug,output);
