#!/usr/bin/env python3
"""Install/remove the local user launchd job. Does not run an upload now."""
import argparse,datetime,os,plistlib,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
LABEL='work.madogiwa.shorts-nightly';DEST=Path.home()/'Library/LaunchAgents'/f'{LABEL}.plist';DOMAIN=f'gui/{os.getuid()}'
def main():
 p=argparse.ArgumentParser();p.add_argument('--remove',action='store_true');a=p.parse_args()
 if a.remove:
  subprocess.run(['launchctl','bootout',DOMAIN+'/'+LABEL],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  DEST.unlink(missing_ok=True);print('Removed',LABEL);return
 if datetime.datetime.now().astimezone().utcoffset()!=datetime.timedelta(hours=9):raise SystemExit('Set this Mac system timezone to Asia/Tokyo before installing')
 logs=ROOT/'.local/shorts-nightly';logs.mkdir(parents=True,exist_ok=True)
 job={'Label':LABEL,'ProgramArguments':[sys.executable,str(HERE/'run.py'),'--execute'],'WorkingDirectory':str(ROOT),'EnvironmentVariables':{'PATH':'/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin','TZ':'Asia/Tokyo'},'StartCalendarInterval':[{'Hour':23,'Minute':n} for n in [0,10,20,30,40,50]],'RunAtLoad':False,'ProcessType':'Background','StandardOutPath':str(logs/'launchd.log'),'StandardErrorPath':str(logs/'launchd-error.log')}
 subprocess.run(['launchctl','bootout',DOMAIN+'/'+LABEL],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 DEST.parent.mkdir(parents=True,exist_ok=True);DEST.write_bytes(plistlib.dumps(job));subprocess.run(['plutil','-lint',str(DEST)],check=True)
 subprocess.run(['launchctl','bootstrap',DOMAIN,str(DEST)],check=True)
 print('Installed',LABEL,'daily 23:00 JST; retries/checks until 23:50. RunAtLoad=false.')
if __name__=='__main__':main()
