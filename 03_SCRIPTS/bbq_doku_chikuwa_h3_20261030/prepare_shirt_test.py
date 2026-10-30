import json,hashlib,zipfile,shutil,subprocess,sys
from pathlib import Path
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1];SK=ROOT/'.claude/skills/minimax-h3-video/scripts'
plan=json.loads((EP/'shirt_test_plan_v1.json').read_text())
job=EP/'generated/h3-shirt-prompt-test-v1';job.mkdir(exist_ok=False);bundle=job/'bundle';bundle.mkdir()
for c in plan['variants']:
 for asset in [c['image'],*c['audio']]:shutil.copy2(EP/asset,bundle/asset)
 prompt=bundle/(c['id']+'.txt');shutil.copy2(EP/c['prompt'],prompt)
 args=[sys.executable,str(SK/'build_workflow.py'),'--mode','r2v','--profile','480p-turbo','--frames',str(c['frames']),'--seed',str(c['seed']),'--prefix','video/shirt_'+c['variant'],'--image',c['image'],'--prompt-file',str(prompt),'--out',str(bundle/(c['id']+'.json'))]
 for f in c['audio']:args+=['--audio',f]
 subprocess.run(args,check=True)
(bundle/'chapter_plan.json').write_text(json.dumps(plan['variants'],ensure_ascii=False,indent=2))
shutil.copy2(EP/'colab_batch.py',bundle/'colab_remote.py')
for f in ['setup_cuda.py','run_workflow.py']:shutil.copy2(SK/f,bundle/f)
with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(bundle.iterdir()):z.write(p,p.name)
(job/'job.json').write_text(json.dumps({'status':'prepared','bundle_sha256':hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest()},indent=2))
print('PREPARED',job)
