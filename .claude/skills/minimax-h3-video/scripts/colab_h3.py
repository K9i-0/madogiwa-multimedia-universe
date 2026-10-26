#!/usr/bin/env python3
"""H3 on official Colab CLI: prepare, run/resume, status, fetch, stop. No browser automation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent


def save(path, value):
    tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(value,indent=2)+'\n'); tmp.replace(path)


def prepare(workflow, job):
    graph=json.loads(workflow.read_text())
    cond=[n for n in graph.values() if n['class_type'] in ('MiniMaxH3ImageToVideo','MiniMaxH3ReferenceToVideo')]
    if len(cond)!=1:
        raise ValueError('Expected exactly one H3 conditioning node')
    inputs={}
    reserved={'workflow.json','setup_cuda.py','run_workflow.py','colab_remote.py','status.json','results.zip'}
    for n in graph.values():
        key={'LoadImage':'image','LoadAudio':'audio'}.get(n['class_type'])
        if key:
            name=n['inputs'][key]
            if Path(name).name!=name or name in reserved:
                raise ValueError('Input must be a flat, non-reserved filename: '+name)
            inputs[name]=(workflow.parent/name).read_bytes()
    job.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(job/'inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('workflow.json',json.dumps(graph))
        for n in ('setup_cuda.py','run_workflow.py','colab_remote.py'):
            z.write(HERE/n,n)
        for n,data in inputs.items(): z.writestr(n,data)
    save(job/'job.json',{'status':'prepared','bundle_sha256':hashlib.sha256((job/'inputs.zip').read_bytes()).hexdigest()})


def cli(*args, stdin=None):
    subprocess.run(['colab','--auth','oauth2',*map(str,args)],input=stdin,text=True,check=True)


def fetch(job,state):
    cli('download','-s',state['session'],state['root']+'/results.zip',job/'results.zip')
    with zipfile.ZipFile(job/'results.zip') as z:
        if any(Path(n).name!=n for n in z.namelist()): raise ValueError('Unexpected archive paths')
        z.extractall(job/'results')
    report=json.loads((job/'results/status.json').read_text())
    if report['status']!='complete': raise RuntimeError('Remote job failed; diagnostics saved under results/')
    for name,digest in report['sha256'].items():
        if hashlib.sha256((job/'results'/name).read_bytes()).hexdigest()!=digest: raise ValueError('Checksum mismatch: '+name)
    state['status']='downloaded'; save(job/'job.json',state)
    print('Verified downloads:',job/'results')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('prepare');q.add_argument('workflow',type=Path);q.add_argument('--job',type=Path,required=True)
    for cmd in ('run','status','fetch','stop'):
        q=sub.add_parser(cmd);q.add_argument('--job',type=Path,required=True)
        if cmd=='run':
            q.add_argument('--session');q.add_argument('--gpu',choices=['L4','A100'],default='L4');q.add_argument('--keep',action='store_true')
    a=p.parse_args()
    if a.cmd=='prepare':
        prepare(a.workflow,a.job);print('Prepared:',a.job);return
    if not shutil.which('colab'):p.error('Install: uv tool install google-colab-cli==0.7.5')
    state_path=a.job/'job.json';state=json.loads(state_path.read_text())
    if a.cmd!='run' and 'session' not in state:
        p.error('This job has not allocated a session yet')
    if a.cmd=='run':
        if a.session and state.get('session') and a.session!=state['session']:
            p.error('Resume must use the original session')
        if hashlib.sha256((a.job/'inputs.zip').read_bytes()).hexdigest()!=state['bundle_sha256']:p.error('Bundle changed; prepare a new job')
        if state['status']=='stopped':p.error('Session stopped; prepare a new job for a new generation')
        if state['status']=='downloaded':
            print('Results already downloaded; use stop to release the session.');return
        if state['status']=='prepared':
            if not a.session or not re.fullmatch(r'[a-zA-Z0-9_-]+',a.session):p.error('First run requires a unique --session using letters/digits/_/-')
            state.update(status='allocating',session=a.session,root='/content/'+a.session)
            save(state_path,state)
            cli('new','-s',a.session,'--gpu',a.gpu,'--high-mem')
            state['status']='allocated';save(state_path,state)
        elif state['status']=='allocating':
            p.error('Allocation response was uncertain. Inspect colab sessions; reconcile job.json with the existing session before resuming. Do not allocate twice.')
        cli('upload','-s',state['session'],a.job/'inputs.zip','/content/'+state['session']+'.zip')
        root=state['root']
        boot='import zipfile\nfrom pathlib import Path\np=Path('+repr(root)+')\np.mkdir(exist_ok=True)\nwith zipfile.ZipFile('+repr(root+'.zip')+') as z:\n    source=z.read("colab_remote.py").decode()\nns={"__name__":"mmu_remote"}\nexec(compile(source,"colab_remote.py","exec"),ns)\nns["main"](str(p))\n'
        (a.job/'execute.py').write_text(boot)
        state['status']='running';save(state_path,state)
        try:
            cli('exec','-s',state['session'],'--timeout','10800','-f',a.job/'execute.py')
            fetch(a.job,state)
        except (subprocess.CalledProcessError,KeyboardInterrupt):
            print('Session preserved. Use status/fetch or run with the same --job; no new prompt is submitted on resume.',file=sys.stderr)
            raise
        if not a.keep:
            cli('stop','-s',state['session']);state['status']='stopped';save(state_path,state)
    elif a.cmd=='status':
        print(json.dumps(state,indent=2))
        cli('status','-s',state['session'])
        cli('download','-s',state['session'],state['root']+'/status.json',a.job/'remote-status.json')
        print((a.job/'remote-status.json').read_text())
    elif a.cmd=='fetch':fetch(a.job,state)
    else:
        if state['status']!='downloaded':p.error('Fetch and verify results before stopping. For an abandoned failed run use colab stop -s SESSION explicitly after collecting logs.')
        cli('stop','-s',state['session']);state['status']='stopped';save(state_path,state)


if __name__=='__main__':main()
