import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill} from '@remotion/renderer';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {mkdirSync} from 'node:fs';
const p=dirname(fileURLToPath(import.meta.url));
const out=resolve(p,'../../00_TEMPLATES/characters/commentary_duo_v1/exports');mkdirSync(out,{recursive:true});
const serveUrl=await bundle({entryPoint:resolve(p,'src/index.ts'),publicDir:resolve(p,'public')});
const moods=['normal','happy','surprise','worry','bored','angry','sad','smug'];
for(const [who,id] of [['takosan','TakosanSprites'],['yametaro','YametaroSprites']]){
 const composition=await selectComposition({serveUrl,id});
 for(let frame=0;frame<16;frame++){
  const output=resolve(out,`${who}_${moods[Math.floor(frame/2)]}_${frame%2?'open':'closed'}.png`);
  await renderStill({serveUrl,composition,output,frame,imageFormat:'png'});
  console.log(output);
 }
}
