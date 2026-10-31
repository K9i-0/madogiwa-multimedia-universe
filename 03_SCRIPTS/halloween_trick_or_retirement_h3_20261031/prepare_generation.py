"""Build four H3 480p Turbo R2V shots, canonical voice-timbre references."""
import hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
EP=Path(__file__).resolve().parent
ROOT=EP.parents[1]
SCRIPTS=ROOT/'.claude/skills/minimax-h3-video/scripts'
IDENTITY=(ROOT/'02_CHARACTERS/references/yametaro-identity-prompt.md').read_text().split('```text\n')[1].split('```')[0].replace('[IMAGE REFERENCE]','<Picture 2>')
COMMON="""A cinematic Japanese Halloween office comedy, widescreen, photographic set with canonical stylized 3D companions. Picture 1 specifies this scene's cast, composition, costume and props; Picture 2 is ONLY Yametaro identity reference, never reproduce its panels or add extra copies. Keep cast of Picture 1 only.
Sobaya, where present, is the same broad muscular man with short black hair, neutral gray exposed skin and rigid opaque white mask with red marks and forehead dot. Distressed brown work jacket and trousers over white cotton shirt. The mask remains properly fitted, its surface and painted mouth never articulate or reveal a face. Voice comes from behind rigid mask; acting through neck, posture and arms. Shirt is uninterrupted opaque cotton with subtle grain, broad soft light gradients and natural folds, unchanged throughout motion.
Takosan where present is small, black hood, white face, round black eyes, two human-shaped arms with rounded white mitten hands, SIX radial lower tentacles, never human legs. Yametaro wears oval charcoal debug-bug costume with six fake side legs and antennae; his real hands remain distinct, canonical compact toy body and opaque white spectacle areas.
No added people, narrator, captions, subtitles, watermark or background music. Only specified Japanese lines and realistic scene sound. Audio references are voice TIMBRE only, not the words or performance to copy. Finish each line before another speaker except explicit simultaneous shout."""
CHAPTERS=[
dict(id='ch01',frames=192,image='input_entrance.png',audio=[],action="""Eight-second horror-comedy entrance. Picture 1 shows the END STATE after destruction, NOT the beginning. Start inside the office aimed at the same doorway with an INTACT CLOSED light wood door, all three characters initially hidden behind it. Loud gasoline chainsaw revving from behind the door. Metal saw blade punches through the wood at waist height, moves down through wood throwing sawdust, then door breaks and falls inward onto the floor with a loud crash. Reveal EXACTLY Sobaya in center gripping orange chainsaw with both hands, Takosan left with scythe and Yametaro right with candy bag, matching Picture 1. Trio take a small step into doorway and stop in proud Halloween pose. End with fallen door on floor and all three clearly visible. Do not start with already broken door. Physical cutting, splinters and actual door collapse are the essential action. No speech, no screams, no injury or blood. Chainsaw engine sound and wooden crash, then engine idles."""),
dict(id='ch02',frames=260,image='input_entrance.png',audio=['voice_sobaya.wav','voice_takosan.wav','voice_yametaro.wav'],action="""Start AFTER the door has broken, as Picture 1; door remains fallen. Same three characters only, medium-wide locked shot. Sobaya holds chainsaw in both hands at waist pointed away from friends; Takosan holds scythe upright; Yametaro holds orange EMPTY candy bag. Audio 1 Sobaya, Audio 2 Takosan, Audio 3 Yametaro are canonical voice timbres. All THREE shout cheerfully together exactly once <d>[Japanese] トリック・オア・退職！</d>. Sobaya then alone says from behind unchanged mask <d>[Japanese] お菓子をくれなきゃ、退職しちゃうぞ！</d>. Other two remain silent, Yametaro extends the same candy bag eagerly. Sobaya switches chainsaw engine off; abrupt engine sputter to silence. Hold eager expectant poses for a beat. No further destruction, no prop swapping, no extra dialogue."""),
dict(id='ch03',frames=362,image='input_fired.png',audio=['voice_yametaro.wav'],action="""15-second locked medium two-shot, Tokun left at desk and Yametaro right, only two characters. Tokun is exact same real Japanese man, same blue-tinted glasses, navy suit, white shirt, tie, employee badge, natural face and build. The door in background is visibly destroyed and remains so. His speaking voice is natural adult Japanese man, low-mid pitch, calm dry matter-of-fact CEO, not a voice from Audio 1. Audio 1 belongs ONLY to Yametaro, soft Kansai male voice.
Tokun first glances toward broken door then looks at Yametaro and says evenly <d>[Japanese] うん。三人ともクビです。</d>. ONE FULL SECOND awkward silence. Yametaro lowers the orange candy bag a little and protests <d>[Japanese] いや、そこはお菓子くれる流れやん。</d>. Tokun waits until the protest is finished, gestures toward broken door, replies <d>[Japanese] 会社のドア壊したよね？</d>. Yametaro freezes with same white spectacle lenses and deflated posture. End on awkward silence, both mouths closed. No extra words, no offscreen replies, no upbeat laughter. Quiet office room tone."""),
dict(id='ch04',frames=362,image='input_outside.png',audio=['voice_yametaro.wav','voice_sobaya.wav'],action="""15-second final continuous medium-wide shot outside office building at dusk. Same THREE friends in Halloween costumes, now fired, cardboard personal-belonging boxes already present. Positions and props exactly Picture 1. Sobaya left holds box; chainsaw engine OFF and resting on ground. Takosan center holds small box, scythe leaning against wall. Yametaro right holds orange bag with WHITE DISMISSAL DOCUMENTS and no candy, his small box at feet. No walking or transfers.
Yametaro looks into his bag, raises face and complains in Audio 1 canonical Kansai voice <d>[Japanese] お菓子もろてへんのに、イタズラされたんワイらやん。</d>. Sobaya listens silently behind unchanged mask, then straightens optimistically and replies in Audio 2 canonical deep voice <d>[Japanese] 明日から毎日ハロウィンできますね！</d>. His mask does not articulate. Takosan silently slowly turns white face toward Sobaya and holds deadpan stare. Yametaro lowers shoulders. End on 2 seconds silent comic tableau. Only distant city ambience and rustle of paper. No extra words or music, no captions. All boxes, tools and documents retain count and position.""")
]
def main():
 job=EP/'generated/h3-v1'; job.mkdir(parents=True,exist_ok=False)
 bundle=job/'bundle';bundle.mkdir()
 shutil.copy2(ROOT/'03_SCRIPTS/00_TEMPLATES/characters/character_yametaro_basic_sheet.png',EP/'identity_yametaro.png')
 for who,source in [('sobaya','Sobaya'),('takosan','Takosan'),('yametaro','Yametaro')]:
  shutil.copy2(ROOT/'02_CHARACTERS'/f'{source}_voice.wav',EP/f'voice_{who}.wav')
 for i,ch in enumerate(CHAPTERS):
  p='\n\n'.join([COMMON,IDENTITY,ch['action']])+'\n'
  (EP/f'prompt_{ch["id"]}_v1.txt').write_text(p)
  (bundle/f'{ch["id"]}.txt').write_text(p)
  for asset in [ch['image'],'identity_yametaro.png',*ch['audio']]:shutil.copy2(EP/asset,bundle/asset)
  ch['seed']=2026103101+i
  args=[sys.executable,str(SCRIPTS/'build_workflow.py'),'--mode','r2v','--profile','480p-turbo','--frames',str(ch['frames']),'--seed',str(ch['seed']),'--prefix','video/halloween_'+ch['id'],'--out',str(bundle/(ch['id']+'.json')),'--prompt-file',str(bundle/(ch['id']+'.txt')),'--image',ch['image'],'--image','identity_yametaro.png']
  for asset in ch['audio']:args+=['--audio',asset]
  subprocess.run(args,check=True)
  shutil.copy2(bundle/(ch['id']+'.json'),EP/(ch['id']+'_workflow.json'))
 (EP/'chapter_plan.json').write_text(json.dumps(CHAPTERS,ensure_ascii=False,indent=2)+'\n')
 shutil.copy2(EP/'chapter_plan.json',bundle/'chapter_plan.json')
 shutil.copy2(EP/'colab_batch.py',bundle/'colab_remote.py')
 for name in ['setup_cuda.py','run_workflow.py']:shutil.copy2(SCRIPTS/name,bundle/name)
 with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(bundle.iterdir()):z.write(p,p.name)
 (job/'job.json').write_text(json.dumps({'status':'prepared','bundle_sha256':hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest()},indent=2)+'\n')
 print('Prepared',job,flush=True)
if __name__=='__main__':main()

