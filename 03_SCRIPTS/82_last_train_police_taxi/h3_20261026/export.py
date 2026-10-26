"""Join the two generated chapters without changing their frame counts; upscale once."""
from pathlib import Path
import subprocess
import json
base=Path(__file__).resolve().parent
inputs=[base/'generated'/f'ch{n}_480p.mp4' for n in (1,2)]
for path in inputs:
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))
    video=next(s for s in info['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height'],video['nb_frames'],video['r_frame_rate'])==(864,480,'362','24/1')
frames=362; duration=frames/24
filters=[]
for i in range(2):
    filters.append(f'[{i}:v]trim=end_frame={frames},setpts=PTS-STARTPTS[v{i}]')
    filters.append(f'[{i}:a]atrim=duration={duration},asetpts=PTS-STARTPTS,apad=whole_dur={duration}[a{i}]')
filters.append('[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]')
filters.append('[v]scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1[out]')
cmd=['ffmpeg','-y','-v','error']
for path in inputs:cmd+=['-i',str(path)]
cmd+=['-filter_complex',';'.join(filters),'-map','[out]','-map','[a]','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(base/'h3_last_train_720p.mp4')]
subprocess.run(cmd,check=True)
