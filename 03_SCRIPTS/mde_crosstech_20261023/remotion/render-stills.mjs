import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill} from '@remotion/renderer';
import fs from 'node:fs';
const manifest=JSON.parse(fs.readFileSync('src/edit-manifest.json','utf8'));
const serveUrl=await bundle({entryPoint:'src/index.ts'});
const composition=await selectComposition({serveUrl,id:'MDECrosstech'});
fs.mkdirSync('out/audit',{recursive:true});
const selected=process.argv.slice(2);
for(const scene of manifest.scenes){
 if(selected.length&&!selected.includes(scene.id))continue;
 const frame=scene.start+Math.floor(scene.duration*.55);
 await renderStill({serveUrl,composition,frame,output:`out/audit/${scene.id}.png`,imageFormat:'png'});
 console.log(scene.id,frame);
}
