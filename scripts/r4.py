#!/usr/bin/env python3
"""Same lightweight workspace commands on macOS and Ubuntu."""
import argparse,hashlib,json,os,platform,re,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
from verify_repository import verify,refresh,files
from privacy_check import scan

def git(*args,check=True,capture=False):
    return subprocess.run(['git','-C',str(ROOT),*args],check=check,text=True,capture_output=capture)

def main():
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest='action',required=True)
    sp.add_parser('doctor');sp.add_parser('verify');sp.add_parser('update')
    n=sp.add_parser('new');n.add_argument('--name',required=True);n.add_argument('--engine',choices=('mujoco','gazebo','real'),required=True);n.add_argument('--seed',type=int,default=42)
    s=sp.add_parser('sync');s.add_argument('--message',required=True)
    review=sp.add_parser('review-media');review.add_argument('--file',required=True,type=Path);review.add_argument('--confirm-reviewed',action='store_true',required=True)
    a=p.parse_args()
    if a.action=='doctor':
        info={'platform':platform.system(),'architecture':platform.machine(),'python':platform.python_version(),'git':bool(shutil.which('git')),'gh':bool(shutil.which('gh')),'ros_jazzy':Path('/opt/ros/jazzy/setup.bash').exists(),'cloud_runner':os.environ.get('R4_CLOUD')=='1','repo_kind':json.loads((ROOT/'.r4.json').read_text())['kind']}
        print(json.dumps(info,indent=2));return
    if a.action=='verify':raise SystemExit(0 if verify() else 1)
    if a.action=='new':
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,48}',a.name):p.error('name must contain only letters, numbers, _ or -')
        runid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+a.name
        dst=ROOT/'runs'/runid;dst.mkdir(parents=True)
        (dst/'run.json').write_text(json.dumps({'run_id':runid,'engine':a.engine,'seed':a.seed,'status':'planned','simulation_only':a.engine!='real','gpu_execution':'cloud_only'},indent=2)+'\n')
        print(dst.relative_to(ROOT));return
    if a.action=='review-media':
        f=(ROOT/a.file).resolve()
        try:rel=f.relative_to(ROOT).as_posix()
        except ValueError:p.error('file must be inside this checkout')
        if not f.is_file():p.error('file does not exist')
        path=ROOT/'metadata/reviewed_binary.json';data=json.loads(path.read_text())
        data[rel]=hashlib.sha256(f.read_bytes()).hexdigest()
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        print('Recorded manual content review:',rel);return
    if a.action=='update':git('pull','--ff-only');return
    if a.action=='sync':
        if json.loads((ROOT/'.r4.json').read_text())['kind']!='lab':p.error('sync is for the private lab; publish a reviewed export separately')
        remote=git('remote','get-url','origin',capture=True).stdout.strip()
        if not remote.endswith(('/r4-mobile-manipulation-lab.git','/r4-mobile-manipulation-lab',':r4-mobile-manipulation-lab.git')):p.error('origin is not the expected private lab repository')
        if scan(ROOT,files()):p.error('privacy preflight failed; run verify for details')
        refresh()
        if not verify():raise SystemExit(1)
        git('add','--all')
        if git('diff','--cached','--quiet',check=False).returncode==1:git('commit','-m',a.message)
        branch=git('branch','--show-current',capture=True).stdout.strip()
        if not branch:p.error('detached HEAD; select a branch first')
        git('push','origin',branch)
if __name__=='__main__':main()
