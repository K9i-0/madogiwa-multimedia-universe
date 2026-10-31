"""Extract representative source video frames for visual audit."""
from pathlib import Path
import subprocess,sys
EP=Path(__file__).resolve().parent
out=EP/'generated/audit';out.mkdir(parents=True,exist_ok=True)
for arg in sys.argv[1:]:
 p=Path(arg)
 dest=out/(p.stem+'_contact.jpg')
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(p),'-vf','fps=1/2,scale=432:240,tile=4x2','-frames:v','1',str(dest)],check=True)
 print(dest,flush=True)
