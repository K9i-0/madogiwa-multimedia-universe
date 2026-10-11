import {execFileSync} from 'node:child_process';
execFileSync('npx',['remotion','render','src/shorts.tsx','SobaSharkShorts','out/shorts_silent.mp4','--codec=h264','--crf=18','--concurrency=2','--muted','--overwrite'],{stdio:'inherit'});
execFileSync('ffmpeg',['-v','error','-i','out/shorts_silent.mp4','-i','../final_remotion_daichikuwa.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart','-y','../final_remotion_shorts_9x16.mp4'],{stdio:'inherit'});
