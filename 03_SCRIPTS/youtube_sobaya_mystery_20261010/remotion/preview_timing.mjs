import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill} from '@remotion/renderer';
import fs from 'node:fs';
const m=JSON.parse(fs.readFileSync('src/edit-manifest.json','utf8'));
const at=id=>m.visualCues[id].frame;
const points=[
 ['portal_before',at('portal_first_start')-1],
 ['portal_first_moving',Math.round((at('portal_first_start')+at('portal_first_end'))/2)],
 ['portal_first_finished',at('portal_first_end')+8],
 ['portal_second_before',at('portal_second_start')-1],
 ['portal_second_moving',Math.round((at('portal_second_start')+at('portal_second_end'))/2)],
 ['portal_second_finished',at('portal_second_end')+8],
 ...['height_measure','height_small','repeat_result','tautology_result','dating_result','film_impression','water_result','secret_result','signal_sound','signal_response','signal_conference','future_result'].map(id=>[id,at(id)+8])
];
const serveUrl=await bundle({entryPoint:'src/index.ts'});const composition=await selectComposition({serveUrl,id:'Explainer'});
for(let i=0;i<points.length;i+=3)await Promise.all(points.slice(i,i+3).map(async ([name,frame])=>{await renderStill({serveUrl,composition,frame,output:`out/timing_v7_${name}.png`,logLevel:'error'});}));
fs.writeFileSync('out/timing_frames_v7.json',JSON.stringify(points,null,2));
