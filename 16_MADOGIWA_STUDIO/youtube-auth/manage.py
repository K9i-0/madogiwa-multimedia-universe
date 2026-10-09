#!/usr/bin/env python3
"""Local admin client. Never prints access/refresh tokens or client secrets."""
import argparse,json,os,subprocess,urllib.request,urllib.error
from pathlib import Path
ROOT=Path.home()/'.config/mmu-youtube'
SECRETS=ROOT/'web-secrets.json'
ORIGIN='https://youtube-auth.madogiwa.work'
def save(path,data):
 path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
 os.fchmod(fd,0o600)
 with os.fdopen(fd,'w') as f:json.dump(data,f,ensure_ascii=False,indent=2)
def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['status','invite','access-token','configure']);p.add_argument('--client-json',type=Path);a=p.parse_args()
 cfg=json.loads(SECRETS.read_text())
 if a.command=='configure':
  if not a.client_json:p.error('--client-json is required')
  web=json.loads(a.client_json.read_text()).get('web',{})
  if web.get('project_id')!='madogiwa-youtube-api':p.error('Expected the madogiwa-youtube-api project')
  if ORIGIN+'/callback' not in web.get('redirect_uris',[]):p.error('Missing exact HTTPS callback URI')
  for k in ['client_id','client_secret']:
   if not web.get(k):p.error('Missing OAuth client field')
  cfg.update(GOOGLE_CLIENT_ID=web['client_id'],GOOGLE_CLIENT_SECRET=web['client_secret']);save(SECRETS,cfg)
  here=Path(__file__).resolve().parent
  subprocess.run([str(here.parent/'node_modules/.bin/wrangler'),'secret','bulk',str(SECRETS),'--config','wrangler.jsonc'],cwd=here,check=True)
  print('OAuth client configured. Secret values were not printed.');return
 path={'status':'/admin/status','invite':'/admin/invitations','access-token':'/admin/access-token'}[a.command]
 req=urllib.request.Request(ORIGIN+path,method='GET' if a.command=='status' else 'POST',headers={'Authorization':'Bearer '+cfg['ADMIN_TOKEN'],'User-Agent':'MMU-YouTube-Admin/1.0'})
 try:
  with urllib.request.urlopen(req,timeout=30) as r:data=json.load(r)
 except urllib.error.HTTPError as e:
  print('HTTP',e.code);raise SystemExit(1)
 if a.command=='status':print(json.dumps(data,ensure_ascii=False,indent=2))
 else:
  target=ROOT/('owner-invitation.json' if a.command=='invite' else 'access-token.json');save(target,data)
  print('Saved privately:',target)
  if a.command=='invite':print('Invitation valid for 24 hours; one use. Share only with the channel owner. The URL is in the private file.')
if __name__=='__main__':main()
