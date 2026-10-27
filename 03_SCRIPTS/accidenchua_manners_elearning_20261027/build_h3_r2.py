"""Build four revised Sobaya/Fukuchan scenes. Keep every previous run intact."""
import hashlib,json,math,subprocess,sys,zipfile
from pathlib import Path
from build_h3 import EP,ROOT,SKILL,DESIGN

SCENES={
 'q2': 'A bright quiet Japanese office beside a large window. A construction crane is clearly visible outside. Sobaya sits camera-left in a low office chair, viewed from his left-rear three-quarter angle; his rigid masked profile and left shoulder are clearly visible, but the FRONT of his chest is out of view. A clear beer mug sits low on the side table. Fukuchan is camera-right, holding a plain folder at waist height. His complete unmasked face remains visible. During the first three seconds Fukuchan slowly crosses between Sobaya and the window, his upper body clearly occluding the visible construction crane at Sobaya\'s eye height. He pauses with his back half-turned toward the window. Sobaya leans his head slightly sideways to try to see around him, and says his one line. Fukuchan notices, turns his face toward Sobaya, gives a small silent apologetic nod, lowers his upper body slightly, and steps aside. The crane is visible again. Both adult heads are fully inside the image. Exactly two characters. Static medium two-shot, no camera movement.',
 'q3': 'Two adults sit beside one pale office desk in a bright quiet Japanese office. Fukuchan sits camera-left and Sobaya sits camera-right. BOTH COMPLETE HEADS are at the same height with generous space above. The camera is at seated eye level and looks at both faces from a gentle three-quarter angle. Fukuchan holds one unmarked folder low, below the chest. Sobaya is clearly idle: his laptop is closed, both hands rest loosely at the edge of the desk, a clear beer mug sits beside him. Fukuchan politely turns toward Sobaya and asks his short request. Sobaya looks down at his completely empty work area, then turns his rigid masked head back to Fukuchan and calmly replies. Fukuchan pauses awkwardly. Sobaya\'s forearms and desk edge naturally obscure the lower front of his shirt. Nobody stands up. The folder never covers a face. Locked-off static medium two-shot.',
 'q4': 'Two adults sit beside one pale desk in a bright quiet Japanese office. Fukuchan sits camera-left, Sobaya sits camera-right. Both complete faces and hair are framed with generous headroom, at equal seated height. Sobaya places one plain white finished document on the desk in front of Fukuchan. His forearms remain naturally in front of his lower chest. Fukuchan looks at the document and smiles as he praises him. Sobaya freezes briefly, then gently raises ONE open palm at shoulder height to stop the subject and delivers his short reply behind his perfectly rigid mask. Fukuchan closes his mouth and looks embarrassed. A beer mug remains still on the far right side of the desk. No contact between the two characters, no handshakes. Static medium two-shot.',
 'q5': 'A quiet Japanese office beside a window at late afternoon. Fukuchan sits camera-left at a pale desk and Sobaya sits camera-right in an office chair angled gently toward the window. Frame BOTH COMPLETE adult heads, shoulders, hands, chairs and desk in one stable medium-wide two-shot. Leave sufficient empty headroom for Fukuchan to rise halfway from his chair; his face must remain fully visible at all times. Fukuchan closes his laptop, smiles, says his line and begins rising to return to work. Sobaya remains seated, comfortably leans back a little, gives one small satisfied nod and says his short reply. His arms stay low across his torso and his beer mug stays on the desk. Fukuchan stops half-risen and looks at Sobaya in disbelief. Sobaya turns his masked face toward the window again. No full standing out of frame, no large stretches, no camera movement.'
}

def main():
 d=json.loads((EP/'content.json').read_text());voices=json.loads((EP/'voice-records.json').read_text())
 job=EP/'generated/h3-r2'
 if job.exists():raise FileExistsError('Reuse the existing job with status/run; do not rebuild or resend: '+str(job))
 workflows=[];inputs=set()
 for n,ch in enumerate(d['chapters'][1:],start=2):
  key=ch['id'];assert set(ch['cast'])=={'sobaya','fukuchan'}
  images=['input_fukuchan.png','input_sobaya.png','input_fukuchan_photo.jpg']
  audio=[voices[l['id']]['file'] for l in ch['dialogue']]
  starts=3.0 if key=='q2' else 1.0;beats=[]
  for i,l in enumerate(ch['dialogue']):
   duration=voices[l['id']]['duration']
   who='Fukuchan' if l['speaker']=='fukuchan' else 'Sobaya'
   beats.append(f'At {starts:.2f} to {starts+duration:.2f} seconds, ONLY {who} says exactly once: <d>[Japanese] {l["text"]}</d>. Use <Audio {i+1}> for this line and this speaker only. No repetitions, fillers, added words or further speech.')
   starts+=duration+.65
  frames=max(243,17*math.ceil(((starts+1.0)*24-5)/17)+5)
  if frames>362:raise ValueError('Dialogue too long')
  prompt='\n\n'.join([
   f'A {frames/24:.3f}-second continuous corporate-training comedy scene. Exactly TWO adult characters: Fukuchan and Sobaya. No other characters. No narrator, music, laugh track, subtitles or on-screen text.',
   '<Picture 1> is Fukuchan\'s canonical unmasked character sheet. <Picture 2> is Sobaya\'s canonical sheet. <Picture 3> is Fukuchan\'s real identity photograph, used only for facial identity, hair and body build. Never display a reference sheet, collage, labels or neutral reference background. Start immediately in the office scene.',
   DESIGN['fukuchan']+' Fukuchan wears NO medical mask or face covering. His nose and mouth are fully visible, matching the unmasked close-up faces in Picture 1. Do not copy the photo\'s mask or change him into a different actor.',
   DESIGN['sobaya']+' The white T-shirt has continuous matte fabric across the chest. No paired point shadows or raised nipple shapes. Preserve the broad chest anatomy and natural wrinkles. His rigid white mask never shifts, opens, talks, becomes transparent or reveals a human face.',
   SCENES[key],
   'Soft natural office light and neutral color. Fukuchan remains the photographed human and Sobaya remains the large muscular gray-skinned masked character. Keep the exact same faces, skin tone, clothes, hands and body proportions throughout. No readable text on paper, badge or monitor. Keep both faces out of the top 10% and bottom 20% of the image.',
   ' '.join(beats)+f' After {starts:.2f} seconds, stop all speech. Both hold a quiet reaction with mouths closed. Sobaya always speaks behind his unmoving mask. Fukuchan never mouths Sobaya\'s line.'
  ])+'\n'
  prompt_path=EP/f'prompt_{key}_r2.txt';prompt_path.write_text(prompt)
  workflow=EP/f'{key}_r2_workflow.json'
  cmd=[sys.executable,str(SKILL/'build_workflow.py'),'--mode','r2v','--profile','480p-turbo','--frames',str(frames),'--seed',str(2026102800+n),'--prefix',f'video/mmu_manners_{key}_r2','--prompt-file',str(prompt_path),'--out',str(workflow)]
  for f in images:cmd+=['--image',f]
  for f in audio:cmd+=['--audio',f]
  subprocess.run(cmd,check=True);workflows.append(workflow);inputs.update(images+audio)
 subprocess.run([sys.executable,str(SKILL/'colab_h3.py'),'prepare',str(workflows[0]),'--job',str(job)],check=True)
 with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
  for wf in workflows:z.write(wf,wf.name)
  for f in sorted(inputs):z.write(EP/f,f)
  for f in ('setup_cuda.py','run_workflow.py'):z.write(SKILL/f,f)
  z.write(EP/'h3_remote_batch.py','colab_remote.py')
 (job/'job.json').write_text(json.dumps({'status':'prepared','bundle_sha256':hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest(),'chapters':[f'q{i}_r2' for i in range(2,6)],'revision':2},indent=2)+'\n')
 print('Prepared',job)

if __name__=='__main__':main()
