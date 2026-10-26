from pathlib import Path
import json,hashlib,shutil,subprocess,zipfile
repo=Path.cwd(); ep=repo/'03_SCRIPTS/82_last_train_police_taxi'; src=ep/'h3_20261026'; dest=repo/'.local/h3-episode82/bundle';dest.mkdir(parents=True,exist_ok=True)
skill=repo/'.claude/skills/minimax-h3-video/scripts'
names=['character_sobaya_basic_sheet.png','character_yametaro_basic_sheet.png','character_fukuchan_basic_sheet.png','reference_taxi_japan.png','reference_police_car_tokyo.png','reference_izakaya_drinks_v2.png','voice_ref_sobaya.wav','voice_ref_yametaro.wav','voice_ref_fukuchan.wav']
manifest=[]
for i,name in enumerate(names):
    path=repo/'03_SCRIPTS/00_TEMPLATES/characters'/name if i<3 else ep/name
    shutil.copy2(path,dest/name)
    manifest.append(dict(input=name,source=str(path.relative_to(repo)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
for ch in (1,2):
    args=['python3',str(skill/'build_workflow.py'),'--mode','r2v','--prompt-file',str(src/f'prompt_ch{ch}.txt'),'--frames','362','--seed',str(820925+ch),'--prefix',f'video/episode82_ch{ch}','--out',str(dest/f'ch{ch}.json')]
    for i,n in enumerate(names):args+=['--image' if i<6 else '--audio',n]
    subprocess.run(args,check=True)
for name in ['setup_cuda.py','run_workflow.py']:shutil.copy2(skill/name,dest/name)
(src/'input_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

shutil.copy2(src/'colab_batch.py',dest/'colab_batch.py')
with zipfile.ZipFile(dest.parent/'mmu-h3-ep82.zip','w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted(dest.iterdir()):
        if path.is_file():z.write(path,path.name)
(dest.parent/'bootstrap.py').write_text("import zipfile\nwith zipfile.ZipFile('/content/mmu-h3-ep82.zip') as z:\n    source=z.read('colab_batch.py').decode()\nnamespace={'__name__':'mmu_batch'}\nexec(compile(source, 'colab_batch.py', 'exec'),namespace)\nnamespace['main']('/content/mmu-h3-ep82')\n")
