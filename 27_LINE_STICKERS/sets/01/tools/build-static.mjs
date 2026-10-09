import fs from 'node:fs';
import path from 'node:path';
import {root,work,mag,run,names} from './lib.mjs';
const out=path.join(root,'static'),images=path.join(out,'images');
fs.mkdirSync(images,{recursive:true});
const mapping=[];
function exportPng(src,dest,w,h){
 mag(src,'-trim','+repage','-resize',`${w-20}x${h-20}`,'-gravity','center','-background','none','-extent',`${w}x${h}`,'-colorspace','sRGB','-depth','8','-units','PixelsPerInch','-density','72',`PNG32:${dest}`);
}
for(const [i,name] of names.entries()){
 const src=path.join(root,'stickers',name,'still.png'),cut=path.join(work,`static-${name}.png`);
 mag(src,'-bordercolor','white','-border','1','-alpha','set','-fuzz','3%','-fill','none','-draw','alpha 0,0 floodfill','-shave','1x1',cut);
 const filename=String(i+1).padStart(2,'0')+'.png';
 exportPng(cut,path.join(images,filename),370,320);
 mapping.push({filename,member:name,source:`stickers/${name}/still.png`});
}
exportPng(path.join(work,'static-sobaya.png'),path.join(images,'main.png'),240,240);
const hh=Number(mag('identify','-format','%h',path.join(root,'source/sobaya/caption.png')));
const icon=path.join(work,'static-tab-art.png');
mag(path.join(work,'static-sobaya.png'),'-crop',`400x${400-hh}+0+${hh}`,'+repage',icon);
exportPng(icon,path.join(images,'tab.png'),96,74);
mag('montage',...mapping.map(x=>path.join(images,x.filename)),'-tile','4x2','-geometry','370x320+0+0','-background','#dce8ec',path.join(out,'preview.png'));
const checks=[];
for(const file of [...mapping.map(x=>x.filename),'main.png','tab.png']){
 const p=path.join(images,file),b=fs.readFileSync(p);let animated=false;
 for(let pos=8;pos<b.length;){const size=b.readUInt32BE(pos);if(b.toString('ascii',pos+4,pos+8)==='acTL')animated=true;pos+=size+12;}
 const [w,h,depth]=mag('identify','-format','%w %h %z',p).toString().split(' ').map(Number);
 const target=file==='main.png'?[240,240]:file==='tab.png'?[96,74]:[370,320];
 const alpha=mag(p,'-alpha','extract','-format','%[fx:minima] %[fx:maxima]','info:').toString();
 if(w!==target[0]||h!==target[1]||depth!==8||animated||b.length>1000000||alpha!=='0 1')throw Error('Invalid static PNG: '+file);
 const border=Number(mag(p,'-alpha','extract','-shave','9x9','-format','%[fx:mean]','info:'));
 if(!border)throw Error('Empty image '+file);
 checks.push({file,width:w,height:h,bytes:b.length,animated,transparent:true,depth});
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({variant:'static',mapping,main:'sobaya with caption',tab:'sobaya without caption',checks},null,2)+'\n');
const zip=path.join(out,'line-upload.zip');fs.rmSync(zip,{force:true});
run('zip',['-q',zip,...mapping.map(x=>x.filename),'main.png','tab.png'],{cwd:images});
run('unzip',['-t',zip]);
if(fs.statSync(zip).size>60000000)throw Error('ZIP too large');
console.log('Validated 8 static stickers + main/tab images and upload ZIP.');
