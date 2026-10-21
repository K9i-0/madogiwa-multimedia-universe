"""Restore local BGM and prior-video excerpt. Gameplay capture stays local; see README."""
from pathlib import Path
import shutil,subprocess
P=Path(__file__).resolve().parent
scripts=P.parents[1]
public=P/'public';public.mkdir(exist_ok=True)
source=scripts/'youtube_project_intro_20261019/remotion/public'
for name in ['intro.mp3','main.wav','unity.mp3']:
 target=public/name
 if not target.exists():shutil.copy2(source/name,target)
excerpt=public/'tripo_excerpt.mp4'
if not excerpt.exists():
 subprocess.run(['ffmpeg','-v','error','-y','-ss','80','-i',str(scripts/'youtube_3d_character_workflow_20261014/final_remotion_tripo_workflow_v6.mp4'),'-t','15','-an','-vf','scale=1280:-2:flags=lanczos','-c:v','libx264','-crf','18',str(excerpt)],check=True)
