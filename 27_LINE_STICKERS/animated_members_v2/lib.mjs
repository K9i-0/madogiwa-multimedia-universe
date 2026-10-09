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
const anchors={yumemin:[180,190,140,125]};
const masks={
 yotan:'polygon 230,45 399,45 399,285 300,360 240,335 215,235',
 takosan:'rectangle 0,0 399,215',
 tokun:'rectangle 0,205 93,399 rectangle 315,205 399,399 ellipse 248,185 24,47 0,360',
 yametaro:'rectangle 0,0 399,333',
 fukuchan:'polygon 0,195 150,195 172,260 158,340 110,399 0,399 polygon 262,195 399,195 399,399 280,399 235,285',
 yumemin:'rectangle 0,130 145,295',
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
 ff('-framerate','10','-i',pattern,'-i',pal,'-filter_complex','[0:v][1:v]paletteuse=dither=bayer:bayer_scale=3','-frames:v',frames.length,'-plays','1','-pred','mixed','-f','apng',dest);
 const table=Array.from({length:256},(_,n)=>{for(let j=0;j<8;j++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
 const b=fs.readFileSync(dest);let frame=0;
 for(let p=8;p<b.length;){const len=b.readUInt32BE(p),type=b.toString('ascii',p+4,p+8);if(type==='fcTL'){b.writeUInt16BE(delays[frame++],p+28);b.writeUInt16BE(1000,p+30);let crc=0xffffffff;for(const x of b.subarray(p+4,p+8+len))crc=table[(crc^x)&255]^(crc>>>8);b.writeUInt32BE((crc^0xffffffff)>>>0,p+8+len);}p+=len+12;}
 if(frame!==frames.length)throw Error('Unexpected APNG frame count '+frame);
 fs.writeFileSync(dest,b);fs.unlinkSync(pal);
}
function gif(frames,delays,dest){const args=[];frames.forEach((f,i)=>args.push('(','-delay',delays[i]/10,f,')'));mag(...args,'-background','white','-alpha','remove','-alpha','off','-colors','192','-dither','None','-loop','0','-layers','Optimize',dest);}

export { root,work,run,mag,ff,prepare,apng,gif,names };
