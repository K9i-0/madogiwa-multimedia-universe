"""Prepare one reproducible 4:3, 480p Turbo H3 performance."""
import json, math, shutil, subprocess, sys
from pathlib import Path

EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
SKILL=ROOT/'.claude/skills/minimax-h3-video/scripts'

def main():
    job=EP/'generated/h3-mega-v1'
    if job.exists():raise FileExistsError('Existing job must be resumed, not rebuilt: '+str(job))
    data=json.loads((EP/'content.json').read_text())
    voices=json.loads((EP/'voice-records.json').read_text())
    images=['input_fukuchan.png','input_sobaya.png','input_fukuchan_photo.jpg']
    for source,target in [
        ('03_SCRIPTS/00_TEMPLATES/characters/character_fukuchan_basic_sheet.png',images[0]),
        ('03_SCRIPTS/00_TEMPLATES/characters/character_sobaya_basic_sheet.png',images[1]),
        ('02_CHARACTERS/Fukuchan.jpg',images[2]),
    ]:shutil.copy2(ROOT/source,EP/target)
    t=1.4;beats=[]
    for index,line in enumerate(data['dialogue']):
        duration=voices[line['id']]['duration'];who='Fukuchan' if line['speaker']=='fukuchan' else 'Sobaya'
        beats.append(f'At {t:.2f} to {t+duration:.2f} seconds ONLY {who} speaks exactly once: <d>[Japanese] {line["text"]}</d>. <Audio {index+1}> is the voice and exact line reference for {who} only.')
        t+=duration+1.0
    frames=max(311,17*math.ceil(((t+1.8)*24-5)/17)+5)
    if frames>362:raise ValueError('Dialogue exceeds one H3 scene')
    skin=(ROOT/'02_CHARACTERS/references/fukuchan-skin-standard.md').read_text().split('```text\n')[1].split('```')[0].strip()
    prompt='\n\n'.join([
        f'A {frames/24:.3f}-second continuous LIVE-ACTION Japanese employee-training comedy scene. Aspect ratio 4:3. Exactly TWO adult characters: Fukuchan and Sobaya. This is an intentionally staged fictional training-film skit. No extra actors, no voice-over, no text, no music, no laugh track.',
        '<Picture 1> is Fukuchan\'s canonical character sheet. <Picture 2> is Sobaya\'s canonical sheet. <Picture 3> is Fukuchan\'s real identity photograph. These are identity references only. Do not display any sheet, collage, labels, duplicated people, reference background or drawn illustration. Start directly in the izakaya.',
        'Fukuchan is the same real adult Japanese man in Pictures 1 and 3: the exact same face, medium-length black hair, slim build, black jacket and white graphic T-shirt. Keep his face, nose and mouth unobstructed. No face covering. '+skin,
        'Sobaya is a full-sized broad muscular adult male character, 180cm and 100kg, short black hair. White rigid full-face mask with round black eye holes, long red cheek markings and a black forehead dot, exactly as Picture 2. All exposed neck, ears, arms and hands are neutral gray. Depict him as a real physical masked performer with realistic anatomy, fabric and lighting, not a miniature, cartoon or animated toy. He wears a fitted white short-sleeve T-shirt with natural broad pectoral shading and cloth wrinkles, but NO nipple bumps, nipple outlines, paired dark dots, localized nipple shadows or highlights. His mask stays fully fitted, rigid, opaque and motionless throughout, even while speaking. Never reveal a human face or move the mask mouth. Do not drink or move a glass toward the mask.',
        'A modest Japanese izakaya private room at evening. Plain beige wall, brown wood trim, warm overhead fluorescent light, ordinary wooden dining table, a small plate of edamame and two coasters. No readable menus or posters. Exactly two transparent glass beer mugs containing golden beer and white foam: one ordinary 350ml mug in front of Fukuchan, and one comically huge thick glass MEGA mug with a large handle, approximately 30cm tall and twice the ordinary mug height, in front of Sobaya. The large-versus-small size contrast must be unmistakable from the first frame and remain constant. No third mug and no can.',
        'Locked-off, level, eye-height medium two-shot like a low-budget early-2000s training DVD. Fukuchan sits on CAMERA LEFT, Sobaya on CAMERA RIGHT, both complete heads and hands visible. Generous headroom. Both faces are at the same height, neither is behind the other. Their forearms and the tabletop naturally cover the lower front of their shirts. The mugs are both clearly visible below their faces with no face occlusion. Plain practical lighting, mild flat contrast, casual staged performance. No cinematic camera movement, no rack focus, no dramatic color grading.',
        'Opening action: Fukuchan has both hands around the large mug already resting on the table. He gently slides it just a few centimeters toward Sobaya while speaking his polite line. The ordinary mug remains on the table in front of Fukuchan. Sobaya looks down at the huge mug, looks at the ordinary mug, then turns his masked head toward Fukuchan and asks his question with a small puzzled tilt. He rests one gray hand on the large handle, but does not drink or lift the mug. Fukuchan gives a small courteous smile and nod as if this were standard procedure. Both pause. No mug size changes, spilling, clinking, exaggerated movements or disappearing props.',
        ' '.join(beats)+f' After {t:.2f} seconds, both remain silent for the rest of the scene. Fukuchan closes his mouth before Sobaya speaks and never mouths Sobaya\'s line. Only faint restaurant room tone. No other voices, extra syllables, narration, captions, logos or sound effects.'
    ])+'\n'
    (EP/'prompt_mega_v1.txt').write_text(prompt)
    wf=EP/'mega_v1_workflow.json'
    cmd=[sys.executable,str(SKILL/'build_workflow.py'),'--mode','r2v','--profile','480p-turbo','--width','640','--height','480','--frames',str(frames),'--seed','2026102805','--prefix','video/mmu_mega_dvd_v1','--prompt-file',str(EP/'prompt_mega_v1.txt'),'--out',str(wf)]
    for name in images:cmd+=['--image',name]
    for line in data['dialogue']:cmd+=['--audio',voices[line['id']]['file']]
    subprocess.run(cmd,check=True)
    subprocess.run([sys.executable,str(SKILL/'colab_h3.py'),'prepare',str(wf),'--job',str(job)],check=True)

if __name__=='__main__':main()
