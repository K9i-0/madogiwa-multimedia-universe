/** Isolated preview render: node render_voice_candidates.mjs current aoyama ... */
import path from 'node:path';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {bundle} from '@remotion/bundler';
import {selectComposition,renderMedia,renderStill} from '@remotion/renderer';

const root=path.dirname(fileURLToPath(import.meta.url));
const keys=process.argv.slice(2);
if(!keys.length)throw new Error('Pass current and/or candidate keys.');
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.ts'),publicDir:path.join(root,'public')});
for(const key of keys){
  if(!/^[a-z0-9_]+$/.test(key))throw new Error('Invalid candidate key');
  const candidate=path.join(root,'out/voice-candidates',key);
  const inputProps=JSON.parse(fs.readFileSync(path.join(candidate,'props.json'),'utf8'));
  const composition=await selectComposition({serveUrl,id:'VoiceCandidate',inputProps});
  const visuals=path.join(candidate,'visuals.mp4');
  const output=path.join(root,'..',`preview_voice_${key}.mp4`);
  const audit=path.join(candidate,'frames');fs.mkdirSync(audit,{recursive:true});
  const rows=inputProps.manifest.dialogue;
  const frames=new Set([0,composition.durationInFrames-1]);
  for(const id of ['intro-01','intro-04','intro-08','intro-10','intro-13','main-01','main-03']){
    const row=rows.find(d=>d.id===id);frames.add(row.startFrame+Math.min(15,row.durationInFrames-1));
  }
  const intro=rows.find(d=>d.id==='intro-13');
  frames.add(intro.startFrame+intro.durationInFrames+35);
  for(const frame of frames){
    await renderStill({serveUrl,composition,inputProps,frame,
      output:path.join(audit,`${String(frame).padStart(5,'0')}.png`),imageFormat:'png',logLevel:'error'});
  }
  console.log(`RENDER ${key} ${composition.durationInFrames} frames`);
  let previous=-1;
  await renderMedia({serveUrl,composition,inputProps,outputLocation:visuals,
    codec:'h264',crf:18,muted:true,concurrency:6,logLevel:'error',
    onProgress:({progress})=>{const decile=Math.floor(progress*10);if(decile!==previous){previous=decile;console.log(`${key} ${decile*10}%`);}}});
  execFileSync('ffmpeg',['-v','error','-y','-i',visuals,'-i',path.join(root,'public',inputProps.manifest.audioSrc),
    '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',output]);
  execFileSync('ffmpeg',['-v','error','-i',output,'-f','null','-']);
  const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',output],{encoding:'utf8'}));
  const video=probe.streams.find(s=>s.codec_type==='video');
  const audio=probe.streams.filter(s=>s.codec_type==='audio');
  if(Number(video.nb_read_frames)!==composition.durationInFrames||video.width!==1280||video.height!==720||video.avg_frame_rate!=='30/1'||audio.length!==1||audio[0].sample_rate!=='48000')throw new Error(`Output validation failed: ${key}`);
  fs.writeFileSync(path.join(candidate,'render_record.json'),JSON.stringify({candidate:key,output,composition,
    frameCount:Number(video.nb_read_frames),durationSeconds:composition.durationInFrames/30,
    audioStreams:audio.length,audioSampleRate:48000,fullDecodePassed:true,
    extractedPreviewFrames:[...frames].sort((a,b)=>a-b),subjectiveListening:false,probe},null,2)+'\n');
  console.log(`COMPLETE ${output}`);
}
