import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=path.dirname(fileURLToPath(import.meta.url));
const names=['sobaya','takosan','tokun','yotan','fukuchan','yametaro','okayaman','yumemin'];
const report=[];
for(const name of names){
 const file=path.join(root,name,'sticker.png'),b=fs.readFileSync(file);let count=0,duration=0,plays;
 for(let p=8;p<b.length;){const len=b.readUInt32BE(p),type=b.toString('ascii',p+4,p+8);if(type==='acTL')plays=b.readUInt32BE(p+12);if(type==='fcTL'){count++;duration+=b.readUInt16BE(p+28)/(b.readUInt16BE(p+30)||100);}p+=len+12;}
 const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_entries','stream=width,height,nb_read_frames,pix_fmt','-of','json',file])).streams[0];
 if(probe.width!==320||probe.height!==270||Number(probe.nb_read_frames)!==count||count!==(name==='sobaya'?13:20)||Math.abs(duration-3)>1e-6||plays!==1||b.length>1000000)throw Error('APNG validation failed: '+name);
 for(const f of ['sticker.png','preview.gif'])execFileSync('ffmpeg',['-v','error','-i',path.join(root,name,f),'-f','null','-']);
 const pixels=f=>execFileSync('magick',[path.join(root,'build',name,f),'-depth','8','rgba:-']);
 const first=pixels('display0.png'),last=pixels('display19.png');
 if(!first.equals(last))throw Error('Loop endpoints differ: '+name);
 const headerHeight=Number(execFileSync('magick',['identify','-format','%h',path.join(root,'build',name,'header.png')]));
 const textPixels=i=>execFileSync('magick',[path.join(root,'build',name,`display${i}.png`),'-crop',`400x${headerHeight}+0+0`,'+repage','-depth','8','rgb:-']);
 const title=textPixels(0);for(let i=1;i<20;i++)if(!title.equals(textPixels(i)))throw Error('Caption changed: '+name+' '+i);
 report.push({name,...probe,frames:count,duration,plays,bytes:b.length,decodeVerified:true,loopEndpointsMatch:true,captionPixelsFixed:true});
}
const sheet=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_entries','stream=width,height,nb_read_frames','-show_entries','format=duration,size','-of','json',path.join(root,'all-members-preview.gif')]));
if(sheet.streams[0].width!==1280||sheet.streams[0].height!==640||Number(sheet.format.duration)!==3)throw Error('Preview sheet validation failed');
execFileSync('ffmpeg',['-v','error','-i',path.join(root,'all-members-preview.gif'),'-f','null','-']);
fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify({members:report,sheet},null,2));
console.log(JSON.stringify({members:report.length,allDecoded:true,durationSeconds:3,sheetBytes:Number(sheet.format.size)},null,2));
