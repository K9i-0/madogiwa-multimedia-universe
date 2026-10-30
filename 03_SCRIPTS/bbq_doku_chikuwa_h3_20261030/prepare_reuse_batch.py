"""Prepare a new immutable batch for the explicitly retained A100 session.
Each chapter id must be new; never overwrite an earlier workflow/output on the VM.
"""
import argparse,hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
EP=Path(__file__).resolve().parent;ROOT=EP.parents[1];SK=ROOT/'.claude/skills/minimax-h3-video/scripts'
p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('--job',type=Path,required=True);p.add_argument('--session',required=True);a=p.parse_args()
chapters=json.loads(a.plan.read_text());a.job.mkdir(parents=True,exist_ok=False);bundle=a.job/'bundle';bundle.mkdir()
assert len({c['id'] for c in chapters})==len(chapters)
for c in chapters:
 assert c['id'] not in ['ch01','ch02','ch03'],'Initial comparison ids are reserved'
 for f in [c['image'],*c['audio']]:shutil.copy2(EP/f,bundle/f)
 prompt=bundle/(c['id']+'.txt');shutil.copy2(EP/c['prompt'],prompt)
 args=[sys.executable,str(SK/'build_workflow.py'),'--mode','r2v','--profile','480p-turbo','--frames',str(c['frames']),'--seed',str(c['seed']),'--prefix','video/bbq_'+c['id'],'--image',c['image'],'--prompt-file',str(prompt),'--out',str(bundle/(c['id']+'.json'))]
 for f in c['audio']:args+=['--audio',f]
 subprocess.run(args,check=True)
(bundle/'chapter_plan.json').write_text(json.dumps(chapters,ensure_ascii=False,indent=2))
shutil.copy2(EP/'colab_batch.py',bundle/'colab_remote.py')
for f in ['setup_cuda.py','run_workflow.py']:shutil.copy2(SK/f,bundle/f)
with zipfile.ZipFile(a.job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(bundle.iterdir()):z.write(f,f.name)
(a.job/'job.json').write_text(json.dumps({'status':'allocated','bundle_sha256':hashlib.sha256((a.job/'inputs.zip').read_bytes()).hexdigest(),'session':a.session,'root':'/content/'+a.session,'reuse_reason':'User authorized continued Colab iterations; existing A100 retained after verified first batch.'},indent=2))
print('PREPARED REUSE',a.job)
