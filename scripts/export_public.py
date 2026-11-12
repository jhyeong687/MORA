#!/usr/bin/env python3
"""Export an allowlisted, reviewed snapshot; never push or change visibility."""
import argparse,hashlib,json,shutil,sys,subprocess
from pathlib import Path
from privacy_check import inspect_file
ROOT=Path(__file__).resolve().parents[1]
ALLOWED=('cad/R4/','media/','simulation/','research/','cloud/','scripts/','tests/','docs/FUSION.md','docs/EVIDENCE.md','docs/SYNC.md','docs/PRIVACY.md','docs/ubuntu/','docs/assets/','evidence/ubuntu/figures/','evidence/ubuntu/metadata/','evidence/ubuntu/selected/')
ROOT_FILES={'.gitignore','.gitattributes','requirements-mujoco.txt','requirements-plots.txt','THIRD_PARTY_NOTICES.md'}
REVIEWED={'.png','.jpg','.jpeg','.gif','.mp4','.f3d','.step','.stl','.npz','.pdf','.html'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--target',required=True,type=Path);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    target=a.target.resolve()
    if target==ROOT or ROOT in target.parents:p.error('target must be a separate public checkout')
    approvals=json.loads((ROOT/'metadata/reviewed_binary.json').read_text())
    selected=[];issues=[]
    for f in sorted(ROOT.rglob('*')):
        if not f.is_file():continue
        rel=f.relative_to(ROOT);name=rel.as_posix()
        if not(name in ROOT_FILES or name.startswith(ALLOWED)):continue
        if any(x in ('.git','__pycache__','node_modules','build','generated','runs','results') for x in rel.parts) and not name.startswith('simulation/mujoco/results/'):continue
        errs=inspect_file(f,rel)
        if f.suffix.lower() in REVIEWED and approvals.get(name)!=hashlib.sha256(f.read_bytes()).hexdigest():errs.append('binary_requires_review')
        if errs:issues.append([name,errs])
        selected.append((f,rel))
    print(json.dumps({'files':len(selected),'issues':issues,'dry_run':a.dry_run},indent=2))
    if issues:raise SystemExit(1)
    if a.dry_run:return
    target.mkdir(parents=True,exist_ok=True)
    for src,rel in selected:
        dst=target/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    new_approvals={rel.as_posix():approvals[rel.as_posix()] for _,rel in selected if rel.as_posix() in approvals}
    (target/'metadata').mkdir(exist_ok=True)
    (target/'metadata/reviewed_binary.json').write_text(json.dumps(new_approvals,ensure_ascii=False,indent=2)+'\n')
    subprocess.run([sys.executable,str(target/'scripts/verify_repository.py'),'--refresh'],check=True)
    # Keep the public README, config and Git history independent.
    print('Exported and verified reviewed files. Review deletions/diff, then commit/push manually.')
if __name__=='__main__':main()
