import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=path.dirname(fileURLToPath(import.meta.url));
const args=process.argv.slice(2);
if(args.length && (args.length!==2||args[0]!=='--out'))throw Error('Usage: node build.mjs [--out directory]');
const out=args.length?path.resolve(args[1]):path.join(root,'build');
fs.mkdirSync(out,{recursive:true});
const frames=path.join(out,'frames');fs.mkdirSync(frames,{recursive:true});
const order=[0,1,2,3,2,1,0,1,2,3,2,1,0];
const delays=[...Array(12).fill(90),1920];
const run=(tool,argv)=>execFileSync(tool,argv,{cwd:out});
const ffmpeg=argv=>run('ffmpeg',['-hide_banner','-loglevel','error','-y',...argv]);
const sources=order.map((n,i)=>{
 const source=path.join(root,'inputs',String(n).padStart(2,'0')+'.png');
 fs.copyFileSync(source,path.join(frames,String(i).padStart(2,'0')+'.png'));
 return source;
});
const gif=[];sources.forEach((f,i)=>gif.push('(','-delay',String(delays[i]/10),f,')'));
run('magick',[...gif,'-background','#c5e8ef','-alpha','remove','-alpha','off','-loop','0','preview.gif']);
ffmpeg(['-framerate','10','-i','frames/%02d.png','-vf','palettegen=reserve_transparent=1','-frames:v','1','palette.png']);
ffmpeg(['-framerate','10','-i','frames/%02d.png','-i','palette.png','-filter_complex','[0:v][1:v]paletteuse=dither=bayer:bayer_scale=3','-plays','1','-pred','mixed','-f','apng','sticker.png']);
// Preserve optimized frame rectangles while setting each frame's exact hold duration.
const table=Array.from({length:256},(_,n)=>{for(let j=0;j<8;j++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
const file=path.join(out,'sticker.png'),b=fs.readFileSync(file);let frame=0;
for(let p=8;p<b.length;){
 const len=b.readUInt32BE(p),type=b.toString('ascii',p+4,p+8);
 if(type==='fcTL'){
  b.writeUInt16BE(delays[frame++],p+28);b.writeUInt16BE(1000,p+30);
  let crc=0xffffffff;for(const x of b.subarray(p+4,p+8+len))crc=table[(crc^x)&255]^(crc>>>8);
  b.writeUInt32BE((crc^0xffffffff)>>>0,p+8+len);
 }
 p+=len+12;
}
if(frame!==13||b.length>1000000)throw Error('Invalid APNG frame count or size');
fs.writeFileSync(file,b);
for(const filename of ['preview.gif','sticker.png']){
 const s=JSON.parse(run('ffprobe',['-v','error','-count_frames','-show_entries','stream=width,height,nb_read_frames','-of','json',filename])).streams[0];
 if(s.width!==320||s.height!==270||Number(s.nb_read_frames)!==13)throw Error('Invalid output: '+filename);
 ffmpeg(['-i',filename,'-f','null','-']);
}
console.log(JSON.stringify({out,frames:13,durationMs:3000,apngBytes:b.length,gifBytes:fs.statSync(path.join(out,'preview.gif')).size},null,2));
