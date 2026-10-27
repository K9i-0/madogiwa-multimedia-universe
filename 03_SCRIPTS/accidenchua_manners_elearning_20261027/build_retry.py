"""Repair observed framing in Q2 and Q3, retaining original inputs and runs."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
from build_h3 import EP,ROOT,SKILL,SCENES
REVISED={
 'q2': 'Use a CLOSE TWO-SHOT from behind and to the left of seated Sobaya, at his eye height. Sobaya occupies the left third of the frame, visible from his left shoulder up; his exact masked profile is visible, and the chest front and lower body are outside the frame. Takosan occupies the middle-right foreground at the SAME HEAD HEIGHT as seated Sobaya, very close to the window. Takosan keeps his compact canonical toy body proportions but his black hood is large in this close perspective. Both heads are fully inside the image. A construction crane is visible through the bright window at center-right. At first Sobaya looks at the crane. Takosan slowly moves half a step LEFT, placing his big black hood directly across the visible crane and directly across Sobaya\'s eye-level sightline. The hood top must be ABOVE Sobaya\'s eyes; the crane is visually occluded by the hood. Sobaya shifts his masked head sideways trying to see around the hood and says his line. Takosan then slowly turns his white face toward Sobaya, revealing his exact two black round eyes, tilts his head, and moves aside so the crane becomes visible again. No wide full-body view, no floor-level tiny Takosan, no looking at the audience. Locked-off camera. Exactly two characters.',
 'q3': 'The camera shows BOTH COMPLETE FACES at EQUAL HEAD HEIGHT in one static medium two-shot across a pale office desk. Fukuchan SITS camera-left on a low office chair. Yametaro SITS camera-right on a raised swivel chair with a cushion, lifting his small compact toy body so his face is level with the seated adult. Both heads have generous empty space above and both are fully visible for the ENTIRE clip. Nobody stands up. Do not crop Fukuchan\'s head or show only his torso. A bright office window is behind them. Fukuchan holds one plain white paper weekly calendar with empty gray boxes and no lettering at mid-chest, below both faces. He looks at the empty calendar and gently points to it as he proposes a meeting. Yametaro looks at Fukuchan, raises both small hands in dismay, then speaks his reply. Fukuchan stops pointing and looks awkwardly at Yametaro. Keep the exact white spectacle lenses and stable compact face design. The calendar never obscures either face. A closed laptop rests low on the desk.'
}
workflows=[]
for i,(name,scene) in enumerate(REVISED.items()):
 base=(EP/f'prompt_{name}.txt').read_text()
 updated=base.replace(SCENES[name][0],scene)
 if updated==base:raise ValueError('Scene not replaced')
 # Avoid a contradictory standing-height/raised-chair instruction in the close Q2 framing.
 if name=='q2':updated=updated.replace('Approximately 110cm high here while preserving the sheet proportions.','His compact toy proportions are unchanged; the close perspective places his hood at the seated adult\'s eye height.')
 prompt=EP/f'prompt_{name}_v2.txt';prompt.write_text(updated)
 graph=json.loads((EP/f'{name}_workflow.json').read_text())
 graph['136']['inputs']['prompt']=updated;graph['129']['inputs']['noise_seed']=202610282+i
 graph['92']['inputs']['filename_prefix']=f'video/mmu_manners_{name}_v2'
 wf=EP/f'{name}_v2_workflow.json';wf.write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n');workflows.append(wf)
job=EP/'generated/h3-retry'
subprocess.run([sys.executable,str(SKILL/'colab_h3.py'),'prepare',str(workflows[0]),'--job',str(job)],check=True)
inputs=set()
for wf in workflows:
 for n in json.loads(wf.read_text()).values():
  key={'LoadImage':'image','LoadAudio':'audio'}.get(n['class_type'])
  if key:inputs.add(n['inputs'][key])
with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for wf in workflows:z.write(wf,wf.name)
 for name in inputs:z.write(EP/name,name)
 for name in ('setup_cuda.py','run_workflow.py'):z.write(SKILL/name,name)
 z.write(EP/'h3_remote_batch.py','colab_remote.py')
(job/'job.json').write_text(json.dumps({'status':'prepared','bundle_sha256':hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest(),'chapters':['q2_v2','q3_v2']},indent=2)+'\n')
print('Prepared composition repair:',job)
