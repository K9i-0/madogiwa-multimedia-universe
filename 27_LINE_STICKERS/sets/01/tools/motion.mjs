import fs from 'node:fs';
import path from 'node:path';
import {root,work,mag,ff} from './lib.mjs';
// Registration samples only stationary parts, never the moving hands or head.
const anchors={yotan:[70,70,130,120],takosan:[110,270,185,75],tokun:[85,40,240,90],fukuchan:[145,85,115,105],yametaro:[145,320,115,45]};
const masks={
 yotan:'polygon 230,45 399,45 399,285 300,360 240,335 215,235',
 takosan:'rectangle 0,0 399,215',
 tokun:'rectangle 0,205 93,399 rectangle 315,205 399,399 ellipse 248,185 24,47 0,360',
 yametaro:'rectangle 0,0 399,333',
 fukuchan:'polygon 0,195 150,195 172,260 158,340 110,399 0,399 polygon 262,195 399,195 399,399 280,399 235,285',
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
 const dir=path.join(work,'motion',name);fs.mkdirSync(dir,{recursive:true});
 const six=name==='yotan';
 const src=path.join(root,'source',name,'keyframes.png');
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

export function buildMotion(name){
 const dir=prepare(name);
 const sequence=name==='fukuchan'?[0,0,1,2,3,2,1,0,1,2,3,2,1,0,0,0]:[0,0,1,2,3,3,3,2,1,0,0,0];
 const seqDir=path.join(dir,'sequence'),smoothDir=path.join(dir,'smooth');fs.mkdirSync(seqDir,{recursive:true});fs.mkdirSync(smoothDir,{recursive:true});
 sequence.forEach((k,i)=>fs.copyFileSync(path.join(dir,`key${k}.png`),path.join(seqDir,String(i).padStart(3,'0')+'.png')));
 ff('-framerate','6','-i',path.join(seqDir,'%03d.png'),'-vf','minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none','-pix_fmt','rgb24',path.join(smoothDir,'%03d.png'));
 const smooth=fs.readdirSync(smoothDir).filter(x=>x.endsWith('.png')).sort().map(x=>path.join(smoothDir,x));
 return dir;
}
