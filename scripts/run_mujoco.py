#!/usr/bin/env python3
"""Run one archived motor/physics case on a cloud runner, into a new directory."""
import argparse,json,os,sys,platform,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'simulation/mujoco'

def main():
    p=argparse.ArgumentParser();p.add_argument('--list',action='store_true');p.add_argument('--case');p.add_argument('--out',type=Path);a=p.parse_args()
    cases=json.loads((SOURCE/'results/cases.json').read_text())
    if a.list:
        print('\n'.join(c['id'] for c in cases));return
    if os.environ.get('R4_CLOUD')!='1':p.error('Run physics on the cloud runner with R4_CLOUD=1; --list is read-only.')
    if not a.case or not a.out:p.error('--case and --out are required')
    case=next((c for c in cases if c['id']==a.case),None)
    if case is None:p.error('unknown case; use --list')
    if a.out.exists():p.error('output already exists; use a fresh directory')
    a.out.mkdir(parents=True)
    sys.path.insert(0,str(SOURCE));import run_tests as tests
    tests.P=a.out.resolve()
    model=tests.mj.MjModel.from_xml_path(str(SOURCE/'r4.xml'))
    result=tests.simulate(model,case,traces=True)
    (a.out/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    metadata={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'engine':'mujoco','case':case,'platform':platform.system(),'architecture':platform.machine(),'simulation_only':True,'contact_grasp_verified':False,'model_sha256':hashlib.sha256((SOURCE/'r4.xml').read_bytes()).hexdigest()}
    (a.out/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
