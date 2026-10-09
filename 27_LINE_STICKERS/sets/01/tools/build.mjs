import fs from 'node:fs';
import path from 'node:path';
import {root,work,mag,apng,gif,names} from './lib.mjs';
import {buildMotion} from './motion.mjs';
const reused=['takosan','tokun','yotan','fukuchan','yametaro'];
for(const name of reused)buildMotion(name);
const delays=[...Array(19).fill(90),1290],allFrames={},stats=[];
function transparent(src,dst){mag(src,'-bordercolor','white','-border','1','-alpha','set','-fuzz','3%','-fill','none','-draw','alpha 0,0 floodfill','-shave','1x1',dst);}
function decal(name){
 const [member,...parts]=name.split('-');
 const input=path.join(root,'source',member,parts.join('-')+'.png'),dst=path.join(work,name+'.png');
 if(name==='yametaro-sweat')mag(input,'(', '+clone','-alpha','off','-fx','b>r*1.15 && g>r*1.1 && b>0.55 ? 1 : 0',')','-compose','CopyOpacity','-composite',dst);
 else if(name==='yametaro-lines'){
  mag(input,'-fill','white','-draw','polygon 30,0 48,0 48,33',dst);transparent(dst,dst);
 }else transparent(input,dst);
 return dst;
}
const decals={
 takosan:[['takosan-rays',55,295,140]],
 yotan:[['yotan-rays',65,232,107]],
 fukuchan:[['fukuchan-rays-left',60,28,154],['fukuchan-rays-right',60,310,158]],
 yametaro:[['yametaro-sweat',64,286,98],['yametaro-lines',39,63,248]],
};
for(const list of Object.values(decals))for(const d of list)d[0]=decal(d[0]);
// Extract the white-outlined emphasis marks at the right of Tokun's tablet.
const tokunDecal=path.join(work,'tokun-rays.png');
mag(path.join(root,'source','tokun','rays-source.png'),'(', '+clone','-alpha','off','-fx','((r<0.20 && g<0.20 && b<0.20) || (r>0.92 && g>0.92 && b>0.92)) ? 1 : 0','-fill','black','-draw','rectangle 0,0 25,69 rectangle 0,64 69,69 rectangle 0,0 69,7','-alpha','off',')','-compose','CopyOpacity','-composite',tokunDecal);
mag(tokunDecal,'(',tokunDecal,'-alpha','extract','-threshold','20%','-define','connected-components:area-threshold=100','-define','connected-components:mean-color=true','-connected-components','8','-alpha','off',')','-compose','CopyOpacity','-composite',tokunDecal);
decals.tokun=[[tokunDecal,48,302,259]];
// The body and mallet rotate together around the body center. Rays remain fixed.
const ybase=path.join(work,'yume-static400.png'),ymask=path.join(work,'yume-body-mask.png');
const ybody=path.join(work,'yume-body.png'),yrays=path.join(work,'yume-rays.png');
mag(path.join(root,'source','yumemin','art.png'),'-resize','400x400',ybase);
mag(ybase,'-alpha','extract','-threshold','35%','-define','connected-components:area-threshold=3000','-define','connected-components:mean-color=true','-connected-components','8','-threshold','50%','-morphology','Dilate','Disk:1',ymask);
mag(ybase,'(',ybase,'-alpha','extract',ymask,'-compose','Multiply','-composite','-alpha','off',')','-compose','CopyOpacity','-composite',ybody);
mag(ybase,'(',ybase,'-alpha','extract','(',ymask,'-negate',')','-compose','Multiply','-composite','-alpha','off',')','-compose','CopyOpacity','-composite',yrays);
const yumAngles=[0,5,10,12,8,-10,-38,-52,-52,-48,-50,-52,-42,-30,-18,-8,-2,0,0,0];
const yumArts=yumAngles.map((angle,i)=>{
 const f=path.join(work,`yumemin-rotation${i}.png`);
 mag('-size','480x480','xc:white','(',ybody,'-virtual-pixel','transparent','-define','distort:viewport=480x480-40-40','-distort','SRT',`230,213 1 ${angle} 230,213`,'+repage',')','-geometry','+0+0','-composite',yrays,'-geometry','+40+5','-composite',f);return f;
});
const okayArt=path.join(work,'okayaman-original.png');
mag(path.join(root,'source','okayaman','art.png'),'-resize','500x500','-background','white','-alpha','remove','-alpha','off',okayArt);
for(const name of names){
 const dir=path.join(work,name),out=path.join(root,'stickers',name);fs.mkdirSync(dir,{recursive:true});fs.mkdirSync(out,{recursive:true});
 const header=path.join(dir,'header.png');fs.copyFileSync(path.join(root,'source',name,'caption.png'),header);
 const hh=Number(mag('identify','-format','%h',header));const areaH=400-hh;
 let arts=[];
 if(name==='okayaman')arts=Array(20).fill(okayArt);
 else if(name==='sobaya'){
  const order=[0,1,2,3,2,1,0,1,2,3,2,1];
  arts=Array.from({length:20},(_,i)=>{const f=path.join(dir,`art${i}.png`);mag(path.join(root,'source','sobaya','poses',String(i<12?order[i]:0).padStart(2,'0')+'.png'),f);return f;});
 }else if(name==='yumemin')arts=yumArts;
 else{
  const pd=path.join(work,'motion',name),steps=[0,0,1,1,2,2,3,3,4,5,5,5,4,3,2,1,0,0,0,0];
  const smooth=fs.readdirSync(path.join(pd,'smooth')).filter(x=>x.endsWith('.png')).sort().map(x=>path.join(pd,'smooth',x));
  arts=Array.from({length:20},(_,i)=>name==='yotan'?path.join(pd,`key${steps[i]}.png`):i===0||i===19?path.join(pd,'key0.png'):smooth[Math.round(i/19*(smooth.length-1))]);
 }
 // A common crop across all poses avoids scale and position changes from per-frame trimming.
 let x0=Infinity,y0=Infinity,x1=0,y1=0;
 for(const art of new Set(arts)){
  const [w,h,x,y]=mag(art,'-fuzz','4%','-trim','-format','%w %h %X %Y','info:').toString().split(' ').map(Number);
  x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+w);y1=Math.max(y1,y+h);
 }
 const crop=`${x1-x0}x${y1-y0}+${x0}+${y0}`;const frames=[],line=[];
 for(let i=0;i<20;i++){
  const peak=i<8?(1-Math.cos(Math.PI*i/8))/2:i<11?1:i<19?(1+Math.cos(Math.PI*(i-11)/8))/2:0;
  const zoom=name==='okayaman'?(1+.06*peak)/1.06:1;
  const dw=Math.round(392*zoom),dh=Math.round((areaH-8)*zoom),dst=path.join(dir,`display${i}.png`);
  const args=['-size','400x400','xc:white','(',arts[i],'-crop',crop,'+repage','-resize',`${dw}x${dh}`,')','-gravity','south','-geometry','+0+4','-composite'];
  for(const [f,w,x,y]of decals[name]||[])args.push('(',f,'-resize',`${w}x`,')','-gravity','northwest','-geometry',`+${x}+${y}`,'-composite');
  args.push(header,'-gravity','northwest','-geometry','+0+0','-composite',dst);mag(...args);frames.push(dst);
  const lf=path.join(dir,`line${i}.png`);transparent(dst,lf);mag(lf,'-resize','260x260','-background','none','-gravity','center','-extent','320x270',lf);line.push(lf);
 }
 gif(frames,delays,path.join(out,'preview.gif'));
 if(name==='sobaya')apng(line.slice(0,13),[...Array(12).fill(90),1920],path.join(out,'sticker.png'));
 else apng(line,delays,path.join(out,'sticker.png'));
 fs.copyFileSync(frames[0],path.join(out,'still.png'));allFrames[name]=frames;
 stats.push({name,frames:name==='sobaya'?13:20,durationMs:3000,bytes:fs.statSync(path.join(out,'sticker.png')).size,captionSource:`source/${name}/caption.png`,captionHeight:hh});console.log('Rendered '+name);
}
const sheets=[];for(let i=0;i<20;i++){const dst=path.join(work,`sheet${i}.png`);mag('montage',...names.map(n=>allFrames[n][i]),'-tile','4x2','-geometry','320x320+0+0','-background','white',dst);sheets.push(dst);}
gif(sheets,delays,path.join(root,'all-members-preview.gif'));fs.copyFileSync(sheets[0],path.join(root,'all-members-still.png'));
fs.mkdirSync(path.join(root,'reports'),{recursive:true});
fs.writeFileSync(path.join(root,'reports','render.json'),JSON.stringify({cycleMs:3000,previewLayout:'4x2',previewFrames:20,delays,yumeminRotationDegrees:yumAngles,yumeminPivot:[230,213],okayamanZoom:[1,1.06],members:stats},null,2));
