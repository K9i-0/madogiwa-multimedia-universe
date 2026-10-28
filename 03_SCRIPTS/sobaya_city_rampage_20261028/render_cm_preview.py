from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent
main=P/'final_sobaya_full_ending_30s_16x9.mp4'
end=P.parent/'super_tsurai_sobaya_end_20261003/final_remotion_sobaya_end.mp4'
out=P/'preview_the_sobaya_cm_ending_33s_16x9.mp4'
filters='[0:v]trim=end_frame=900,setpts=PTS-STARTPTS,setsar=1[v0];[0:a]aresample=48000,aformat=channel_layouts=stereo,atrim=end_sample=1440000,asetpts=PTS-STARTPTS,afade=t=out:st=29.95:d=0.05[a0];[1:v]trim=end_frame=90,setpts=PTS-STARTPTS,setsar=1[v1];[1:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=end_sample=144000,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(main),'-i',str(end),'-filter_complex',filters,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(out)],check=True)
(P/'edit_manifest_cm_preview.json').write_text(json.dumps({'main':main.name,'endcard':str(end.relative_to(P.parent)),'output':out.name,'fps':30,'frames':990,'seconds':33,'transition':'hard cut at 30s; 50ms audio tail fade on main only','endcard_audio':'existing Sobaya product call; source endcard audio retained','publication':'preview only'},ensure_ascii=False,indent=2)+'\n')
print(out)
