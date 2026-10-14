import fs from 'node:fs';
import path from 'node:path';
import {root,work,mag,ff,gif,names} from './lib.mjs';
const dir=path.join(work,'black');fs.mkdirSync(dir,{recursive:true});
// Decode delivered APNGs, not intermediate artwork, to audit exported edges.
for(const name of names){
 const d=path.join(dir,name);fs.mkdirSync(d,{recursive:true});
 for(const f of fs.readdirSync(d))fs.unlinkSync(path.join(d,f));
 ff('-i',path.join(root,'stickers',name,'sticker.png'),'-vsync','0',path.join(d,'%02d.png'));
}
for(const background of ['black','white']){
const frames=[];
for(let i=0;i<20;i++){
 const tiles=names.map(name=>{
  const f=path.join(dir,`${background}-${name}-${i}.png`),index=name==='sobaya'?Math.min(i,12):i;
  mag(path.join(dir,name,String(index+1).padStart(2,'0')+'.png'),'-background',background,'-alpha','remove','-alpha','off',f);return f;
 });
 const f=path.join(dir,`${background}-sheet${i}.png`);
 mag('montage',...tiles,'-tile','4x2','-geometry','320x270+0+0','-background',background,f);frames.push(f);
}
gif(frames,[...Array(19).fill(90),1290],path.join(root,`all-members-${background}-preview.gif`));
fs.copyFileSync(frames[0],path.join(root,`all-members-${background}-still.png`));
mag('montage',...names.map((_,i)=>path.join(root,'static/images',String(i+1).padStart(2,'0')+'.png')),'-tile','4x2','-geometry','370x320+0+0','-background',background,'-alpha','remove','-alpha','off',path.join(root,`static/preview-${background}.png`));
}
console.log('Black and white previews rendered from delivered files.');
