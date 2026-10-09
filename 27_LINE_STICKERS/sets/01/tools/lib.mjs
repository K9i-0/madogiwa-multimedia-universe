import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const work=path.join(root,'build');fs.mkdirSync(work,{recursive:true});
const run=(tool,args,opts={})=>execFileSync(tool,args,{maxBuffer:40*1024*1024,...opts});
const mag=(...args)=>run('magick',args.map(String));
const ff=(...args)=>run('ffmpeg',['-hide_banner','-loglevel','error','-y',...args.map(String)]);
const names=["sobaya","takosan","tokun","yotan","fukuchan","yametaro","okayaman","yumemin"];
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

export { root,work,run,mag,ff,apng,gif,names };
