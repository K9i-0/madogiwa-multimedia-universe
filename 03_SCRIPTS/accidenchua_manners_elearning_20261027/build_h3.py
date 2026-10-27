"""Prepare five R2V chapters and one resumable, sequential official-Colab job."""
import hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path

EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
SKILL=ROOT/'.claude/skills/minimax-h3-video/scripts'
SHEETS=ROOT/'03_SCRIPTS/00_TEMPLATES/characters'
NAMES={'sobaya':'Sobaya','fukuchan':'Fukuchan','yametaro':'Yametaro','takosan':'Takosan'}
YAME=(ROOT/'02_CHARACTERS/references/yametaro-identity-prompt.md').read_text().split('```text\n')[1].split('```')[0].strip()
FUKU=(ROOT/'02_CHARACTERS/references/fukuchan-skin-standard.md').read_text().split('```text\n')[1].split('```')[0].strip()
DESIGN={
 'sobaya':'Sobaya is a broad, muscular, 180cm-tall male character with short black hair, uniformly neutral-gray exposed skin and his exact white mask with black eye holes, red markings and black forehead dot. His mask stays fully fitted, opaque and unmoving in every frame, including while he speaks. Never reveal a human face or animate the rigid mask mouth. He wears a fitted white short-sleeve T-shirt, black jeans and white sneakers. Preserve broad chest shading and natural fabric folds, but no nipple bumps, outlines, dots, localized nipple shadows or highlights. One clear beer mug rests in his hand or on the desk; he does not remove his mask to drink.',
 'fukuchan':'Fukuchan is the real photographed adult man from his canonical photo and sheet, not a cartoon or a generic actor. Match his exact face, black hair, facial proportions, slim adult build, black jacket over a white graphic T-shirt, black trousers and blank white badge. No legible lettering on badge or lanyard. '+FUKU,
 'yametaro':'Yametaro is the matte three-dimensional chibi from his sheet, about 90cm tall beside an adult, with a lavender short-sleeve patterned shirt and black trousers. He remains a rounded compact toy with the reference proportions, not a real human. His raised swivel chair brings his head to desktop height. ',
 'takosan':'Takosan is the exact compact matte toy-diorama 3D character from his sheet: large black hood, white round face, two solid black round eyes, two human-positioned arms ending in small white rounded mitten-like hands with no separated fingers, and exactly six lower-body tentacles radiating at roughly 60-degree intervals. Back tentacles may be occluded; do not line all six up in front. Arms never become tentacles. No human legs. Approximately 110cm high here while preserving the sheet proportions. His simple small mouth only moves when his designated dialogue is spoken.'
}
SCENES={
 'q1':('A quiet bright Japanese corporate office beside floor-to-ceiling windows. Sobaya sits camera-right in an office chair, his laptop CLOSED on a pale desk, holding his beer mug low. Fukuchan stands camera-left beside the desk. Medium-wide static two-shot, camera at seated eye level, both faces unobstructed. Fukuchan politely bows and smiles as he greets Sobaya. Sobaya looks at his closed laptop, then turns his rigid masked face toward Fukuchan and responds with a small shrug. Fukuchan becomes awkwardly still. Both remain clearly framed.', 'Fukuchan greets; Sobaya replies.'),
 'q2':('A quiet bright Japanese corporate office beside a large window. Outside, a distant construction crane and unfinished building are clearly visible. Sobaya sits camera-left in a LOW lounge chair facing the window, his beer mug on the side table. Takosan moves slowly from camera-right into the narrow space between Sobaya and the window, carrying one plain unmarked folder, then stops, blocking Sobaya\'s line of sight to the crane. Use a static medium-wide three-quarter side view in which both characters and the window are visible. Sobaya shifts his head gently left then right to see around Takosan and speaks. Takosan silently tilts his head, then shuffles a little aside. Keep the movement slow and simple; no collision, falling or morphing.', 'Only Sobaya speaks; Takosan is silent throughout.'),
 'q3':('A bright quiet Japanese office desk beside a window. Yametaro sits camera-right in a raised swivel chair, looking content. Fukuchan stands camera-left holding one plain white paper weekly calendar with faint empty gray boxes but absolutely no letters or numbers. A closed laptop rests on the desk. Static medium-wide two-shot at desk height. Fukuchan looks at the empty paper and gestures toward it, offering to schedule a meeting. Yametaro turns toward him and raises both small hands in dismay, then says his short reply. Fukuchan pauses, looking between the paper and Yametaro. Do not add visible pupils or change Yametaro\'s glasses.', 'Fukuchan proposes a meeting; Yametaro reacts.'),
 'q4':('A bright quiet Japanese office. Yametaro sits camera-right in a raised chair at a pale desk with a laptop whose lid faces the camera so its screen is never visible. Takosan stands camera-left beside the desk. Static medium-wide two-shot, both toy characters fully recognizable in the real office space. Yametaro places one unmarked white document on the desk in front of Takosan, then briefly straightens with pride. Takosan looks at the document and praises him, using a small natural mouth movement. Yametaro\'s shoulders sink; he raises one palm to gently stop the praise and replies. End with a quiet awkward beat. No high-fives or touching faces.', 'Takosan praises; Yametaro stops the subject.'),
 'q5':('A bright quiet Japanese office beside a large window at late afternoon. Fukuchan sits camera-left at a pale desk, with a laptop open away from camera. Yametaro sits camera-right in a raised swivel chair angled gently toward the window, relaxed. Locked-off medium-wide two-shot. Fukuchan closes the laptop and rises enthusiastically to return to work while speaking. Yametaro remains seated, does a small relaxed stretch without changing body proportions, and delivers his short line. Fukuchan stops standing and looks at Yametaro in disbelief while Yametaro calmly returns his attention to the window. End with both still in frame.', 'Fukuchan returns to work; Yametaro considers his uneventful day complete.')
}

def main():
 d=json.loads((EP/'content.json').read_text());voices=json.loads((EP/'voice-records.json').read_text())
 if d.get('revision',1)>1:raise ValueError('Revision 2 uses build_h3_r2.py; retain the original executed prompts.')
 for key in NAMES:
  shutil.copy2(SHEETS/f'character_{key}_basic_sheet.png',EP/f'input_{key}.png')
 shutil.copy2(ROOT/'02_CHARACTERS/Fukuchan.jpg',EP/'input_fukuchan_photo.jpg')
 workflow_paths=[]
 for i,ch in enumerate(d['chapters']):
  images=[f'input_{name}.png' for name in ch['cast']]
  if 'fukuchan' in ch['cast']:images.append('input_fukuchan_photo.jpg')
  audios=[voices[x['id']]['file'] for x in ch['dialogue']]
  for line in ch['dialogue']:
   if not (EP/voices[line['id']]['file']).is_file():raise FileNotFoundError(line['id'])
  t=1.3;beats=[]
  for j,line in enumerate(ch['dialogue']):
   duration=voices[line['id']]['duration']
   beats.append(f'At {t:.2f}s to {t+duration:.2f}s, ONLY {NAMES[line["speaker"]]} says <d>[Japanese] {line["text"]}</d>, using <Audio {j+1}> as the exact spoken-line and voice reference. Match its natural wording, pacing and timbre; no added words, no other speaker lip movement.')
   t+=duration+0.65
  frames=311 if t+1.2<=311/24 else 362
  if t+0.3>362/24:raise ValueError('Dialogue too long: '+ch['id'])
  parts=[f'This is a {frames/24:.3f}-second single continuous shot for a fictional employee-training comedy. There are exactly TWO characters, '+ ' and '.join(NAMES[n] for n in ch['cast'])+'. No extra people, no duplicate characters.']
  parts+=['Required image inputs: '+'; '.join(f'<Picture {j+1}> = {f}' for j,f in enumerate(images))+'. These are identity references ONLY. Never show any reference sheet, collage, multiple views, neutral sheet background, labels, or freeze-frame of a sheet. Start immediately in the office scene.']
  for j,name in enumerate(ch['cast']):
   parts.append(DESIGN[name])
   if name=='yametaro':parts.append(YAME.replace('[IMAGE REFERENCE]',f'<Picture {j+1}>'))
  parts.append('Photographic corporate-training cinematography, soft natural office daylight, neutral color balance, calm static camera, no dramatic movie lighting. The real adult and the matte toy characters, where present, inhabit the same physical room with matching light and contact shadows. No anime outlines. Keep head, glasses, mask, limbs and hands stable from first to last frame. Keep important faces and gestures away from the top 12 percent and bottom 17 percent for later training graphics. No on-screen words, subtitles, logos, badges with text, watermarks or UI. Do not show a readable computer screen. No music, no narrator, no laugh track; only the specified dialogue and faint office room tone.')
  parts.append(SCENES[ch['id']][0]);parts.append('Performance: '+SCENES[ch['id']][1])
  parts.append('Opening 1.3 seconds: establish the two people and their simple activity. '+' '.join(beats)+f' After {t:.2f}s, hold a quiet reaction with all mouths closed until the end. Every voice belongs only to the assigned character. Sobaya speaks behind his rigid mask; the mask never moves or opens.')
  prompt=EP/f'prompt_{ch["id"]}.txt';prompt.write_text('\n\n'.join(parts)+'\n')
  wf=EP/f'{ch["id"]}_workflow.json'
  cmd=[sys.executable,str(SKILL/'build_workflow.py'),'--mode','r2v','--profile','480p-turbo','--frames',str(frames),'--seed',str(202610270+i),'--prefix',f'video/mmu_manners_{ch["id"]}','--prompt-file',str(prompt),'--out',str(wf)]
  for image in images:cmd+=['--image',image]
  for audio in audios:cmd+=['--audio',audio]
  subprocess.run(cmd,check=True);workflow_paths.append(wf)
 job=EP/'generated/h3-job'
 subprocess.run([sys.executable,str(SKILL/'colab_h3.py'),'prepare',str(workflow_paths[0]),'--job',str(job)],check=True)
 graph_inputs=set()
 for wf in workflow_paths:
  for node in json.loads(wf.read_text()).values():
   key={'LoadImage':'image','LoadAudio':'audio'}.get(node['class_type'])
   if key:graph_inputs.add(node['inputs'][key])
 with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
  for wf in workflow_paths:z.write(wf,wf.name)
  for f in sorted(graph_inputs):z.write(EP/f,f)
  for f in ('setup_cuda.py','run_workflow.py'):z.write(SKILL/f,f)
  z.write(EP/'h3_remote_batch.py','colab_remote.py')
 state={'status':'prepared','bundle_sha256':hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest(),'chapters':[ch['id'] for ch in d['chapters']]}
 (job/'job.json').write_text(json.dumps(state,indent=2)+'\n')
 print('READY',job,flush=True)

if __name__=='__main__':main()
