import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=path.dirname(fileURLToPath(import.meta.url));
const work=path.join(root,'build');fs.mkdirSync(work,{recursive:true});
const run=(tool,args,opts={})=>execFileSync(tool,args,{maxBuffer:40*1024*1024,...opts});
const mag=(...args)=>run('magick',args.map(String));
const ff=(...args)=>run('ffmpeg',['-hide_banner','-loglevel','error','-y',...args.map(String)]);
const font='/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc';
const names=['sobaya','takosan','tokun','yotan','fukuchan','yametaro','okayaman','yumemin'];
const captions={takosan:['興味深い'],tokun:['トークン切れ'],yotan:['お前島流し！'],fukuchan:['ギュンにチュア'],yametaro:['ごめんやで'],okayaman:['大変驚いて','おります！'],yumemin:['起きろ！']};
// Registration samples only stationary parts, never the moving hands or head.
const anchors={yotan:[70,70,130,120],takosan:[110,270,185,75],tokun:[85,40,240,90],fukuchan:[145,85,115,105],yametaro:[145,320,115,45],okayaman:[130,100,145,100],yumemin:[145,165,140,115]};
const masks={
 yotan:'polygon 230,45 399,45 399,285 300,360 240,335 215,235',
 takosan:'rectangle 0,0 399,215',
 tokun:'rectangle 0,205 93,399 rectangle 315,205 399,399 ellipse 248,185 24,47 0,360',
 yametaro:'rectangle 0,0 399,333',
 fukuchan:'polygon 0,195 150,195 172,260 158,340 110,399 0,399 polygon 262,195 399,195 399,399 280,399 235,285',
 yumemin:'polygon 0,0 220,0 220,120 135,138 125,218 0,218',
 okayaman:'polygon 0,170 123,170 150,300 123,399 0,399 polygon 277,170 399,170 399,399 277,399 250,300',
};
function rgb(file){return mag(file,'-alpha','off','-depth','8','rgb:-');}
function registration(base,other,region){
 const [x,y,w,h]=region,points=[];
 for(let py=y;py<y+h;py+=5)for(let px=x;px<x+w;px+=5){const k=(py*400+px)*3;if(Math.min(base[k],base[k+1],base[k+2])<230)points.push([px,py,k]);}
 function score(s,dx,dy){let sum=0,count=0;for(const [px,py,k]of points){const qx=Math.round(px*s+dx),qy=Math.round(py*s+dy);if(qx<0||qx>=400||qy<0||qy>=400)continue;const q=(qy*400+qx)*3;for(let c=0;c<3;c++)sum+=Math.min(80,Math.abs(base[k+c]-other[q+c]));count++;}return count?sum/count:1e9;}
 let best={cost:1e9,s:1,dx:0,dy:0};
 for(const s of [.94,.97,1,1.03,1.06])for(let dx=-36;dx<=36;dx+=4)for(let dy=-36;dy<=36;dy+=4){const cost=score(s,dx,dy);if(cost<best.cost)best={cost,s,dx,dy};}
 const seed={...best};for(let s=seed.s-.015;s<=seed.s+.0151;s+=.005)for(let dx=seed.dx-3;dx<=seed.dx+3;dx++)for(let dy=seed.dy-3;dy<=seed.dy+3;dy++){const cost=score(s,dx,dy);if(cost<best.cost)best={cost,s,dx,dy};}
 return best;
}
function prepare(name){
 const dir=path.join(work,name);fs.mkdirSync(dir,{recursive:true});
 const six=name==='yotan'&&fs.existsSync(path.join(root,'inputs','yotan-six-poses.png'));
 const src=path.join(root,'inputs',six?'yotan-six-poses.png':name+'-keyframes.png');
 const [width,height]=mag('identify','-format','%w %h',src).toString().split(' ').map(Number);
 const cols=six?3:2,count=six?6:4,cw=Math.floor(width/cols),ch=Math.floor(height/2);
 for(let i=0;i<count;i++)mag(src,'-crop',`${cw}x${ch}+${i%cols*cw}+${Math.floor(i/cols)*ch}`,'+repage','-resize','400x400!','-background','white','-alpha','remove','-alpha','off',path.join(dir,`raw${i}.png`));
 const base=rgb(path.join(dir,'raw0.png')),report=[];
 for(let i=0;i<count;i++){
  const dst=path.join(dir,`key${i}.png`);
  if(i===0){fs.copyFileSync(path.join(dir,'raw0.png'),dst);continue;}
  const r=registration(base,rgb(path.join(dir,`raw${i}.png`)),anchors[name]);report.push(r);
  const affine=[1/r.s,0,0,1/r.s,-r.dx/r.s,-r.dy/r.s].join(',');
  mag(path.join(dir,`raw${i}.png`),'-virtual-pixel','white','-define','distort:viewport=400x400+0+0','-distort','AffineProjection',affine,'+repage',dst);
  if(masks[name]){
   const mask=path.join(dir,'motion-mask.png');mag('-size','400x400','xc:black','-fill','white','-draw',masks[name],'-blur','0x2',mask);
   mag(path.join(dir,'raw0.png'),dst,mask,'-composite',dst);
  }
 }
 fs.writeFileSync(path.join(dir,'registration.json'),JSON.stringify(report,null,2));
 return dir;
}
function apng(frames,delays,dest){
 const pal=dest+'.palette.png',pattern=path.join(path.dirname(frames[0]),'line%d.png');
 ff('-framerate','10','-i',pattern,'-vf','palettegen=reserve_transparent=1','-frames:v','1',pal);
 ff('-framerate','10','-i',pattern,'-i',pal,'-filter_complex','[0:v][1:v]paletteuse=dither=bayer:bayer_scale=3','-plays','1','-pred','mixed','-f','apng',dest);
 const table=Array.from({length:256},(_,n)=>{for(let j=0;j<8;j++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
 const b=fs.readFileSync(dest);let frame=0;
 for(let p=8;p<b.length;){const len=b.readUInt32BE(p),type=b.toString('ascii',p+4,p+8);if(type==='fcTL'){b.writeUInt16BE(delays[frame++],p+28);b.writeUInt16BE(1000,p+30);let crc=0xffffffff;for(const x of b.subarray(p+4,p+8+len))crc=table[(crc^x)&255]^(crc>>>8);b.writeUInt32BE((crc^0xffffffff)>>>0,p+8+len);}p+=len+12;}
 if(frame!==frames.length)throw Error('Unexpected APNG frame count '+frame);
 fs.writeFileSync(dest,b);fs.unlinkSync(pal);
}
function gif(frames,delays,dest){const args=[];frames.forEach((f,i)=>args.push('(','-delay',delays[i]/10,f,')'));mag(...args,'-background','white','-alpha','remove','-alpha','off','-colors','192','-dither','None','-loop','0','-layers','Optimize',dest);}
const delays=[...Array(19).fill(90),1290],allFrames={},stats=[];
const selected=process.argv.slice(2);const buildNames=selected.length?selected:names;
for(const name of buildNames){
 const out=path.join(root,name);fs.mkdirSync(out,{recursive:true});
 if(name==='sobaya'){
  const src=path.join(root,'..','sobaya_sake_friends');for(const f of ['sticker.png','preview.gif'])fs.copyFileSync(path.join(src,f),path.join(out,f));
  const dir=path.join(work,name);fs.mkdirSync(dir,{recursive:true});const order=[0,1,2,3,2,1,0,1,2,3,2,1];
  allFrames[name]=Array.from({length:20},(_,i)=>{const dst=path.join(dir,`display${i}.png`);mag('-size','400x400','xc:white','(',path.join(src,'inputs',String(i<12?order[i]:0).padStart(2,'0')+'.png'),'-crop','320x210+0+60','+repage','-trim','+repage','-resize','320x305','-background','white','-alpha','remove',')','-gravity','north','-geometry','+0+86','-composite','-font',font,'-pointsize','52','-fill','black','-gravity','north','-annotate','+0+8','酒は友達',dst);return dst;});
  stats.push({name,reused:true,frames:13,durationMs:3000});continue;
 }
 console.log('Preparing '+name);const dir=prepare(name);
 // Padded endpoints make optical-flow interpolation include both endpoints.
 const sequence=['fukuchan','yumemin'].includes(name)?[0,0,1,2,3,2,1,0,1,2,3,2,1,0,0,0]:[0,0,1,2,3,3,3,2,1,0,0,0];
 const seqDir=path.join(dir,'sequence'),smoothDir=path.join(dir,'smooth');fs.mkdirSync(seqDir,{recursive:true});fs.mkdirSync(smoothDir,{recursive:true});
 sequence.forEach((k,i)=>fs.copyFileSync(path.join(dir,`key${k}.png`),path.join(seqDir,String(i).padStart(3,'0')+'.png')));
 ff('-framerate','6','-i',path.join(seqDir,'%03d.png'),'-vf','minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none','-pix_fmt','rgb24',path.join(smoothDir,'%03d.png'));
 const smooth=fs.readdirSync(smoothDir).filter(x=>x.endsWith('.png')).sort().map(x=>path.join(smoothDir,x));
 const display=[],lineFrames=[];
 for(let i=0;i<20;i++){
  const yotanSteps=[0,0,1,1,2,2,3,3,4,5,5,5,4,3,2,1,0,0,0,0];
  const art=name==='yotan'&&fs.existsSync(path.join(dir,'key5.png'))?path.join(dir,`key${yotanSteps[i]}.png`):i===0||i===19?path.join(dir,'key0.png'):smooth[Math.round(i/19*(smooth.length-1))];
  const dst=path.join(dir,`display${i}.png`);const lines=captions[name];const size=lines.length===2?37:Math.min(52,Math.floor(370/(lines[0].length)));
  mag('-size','400x400','xc:white','(',art,'-resize',lines.length===2?'312x312':'332x332',')','-gravity','north','-geometry',lines.length===2?'+0+85':'+0+65','-composite','-font',font,'-pointsize',size,'-fill','black','-gravity','north','-annotate','+0+8',lines.join('\n'),dst);
  display.push(dst);const line=path.join(dir,`line${i}.png`);
  mag(dst,'-bordercolor','white','-border','1','-alpha','set','-fuzz','3%','-fill','none','-draw','alpha 0,0 floodfill','-shave','1x1','-resize','260x260','-background','none','-gravity','center','-extent','320x270',line);
  lineFrames.push(line);
 }
 gif(display,delays,path.join(out,'preview.gif'));apng(lineFrames,delays,path.join(out,'sticker.png'));
 fs.copyFileSync(display[0],path.join(out,'still.png'));allFrames[name]=display;
 stats.push({name,frames:20,durationMs:3000,bytes:fs.statSync(path.join(out,'sticker.png')).size});
 console.log('Rendered '+name);
}
if(!selected.length){
 const sheet=[];for(let i=0;i<20;i++){const dst=path.join(work,`sheet${i}.png`);mag('montage',...names.map(n=>allFrames[n][i]),'-tile','4x2','-geometry','320x320+0+0','-background','white',dst);sheet.push(dst);}
 gif(sheet,delays,path.join(root,'all-members-preview.gif'));fs.copyFileSync(sheet[0],path.join(root,'all-members-still.png'));
 fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify({cycleMs:3000,previewLayout:'4x2',previewFrames:20,delays,members:stats},null,2));
}
console.log(JSON.stringify(stats,null,2));
