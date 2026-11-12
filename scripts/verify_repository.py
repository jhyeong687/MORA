#!/usr/bin/env python3
"""Validate archive integrity, source syntax and portable model references."""
from pathlib import Path
import ast,hashlib,json,sys,xml.etree.ElementTree as ET
from privacy_check import scan
ROOT=Path(__file__).resolve().parents[1]

def files():
    excluded={'.git','.r4-local','__pycache__','.venv','runs','node_modules'}
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(x in excluded for x in p.relative_to(ROOT).parts))

def refresh():
    data={'schema_version':1,'files':[]}
    for p in files():
        if p.relative_to(ROOT).as_posix()=='metadata/manifest.json':continue
        data['files'].append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    dest=ROOT/'metadata/manifest.json';dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    return len(data['files'])

def verify(check_manifest=True):
    fs=files();errors=scan(ROOT,fs)
    approved_file=ROOT/'metadata/reviewed_binary.json'
    approved=json.loads(approved_file.read_text()) if approved_file.exists() else {}
    reviewed_ext={'.png','.jpg','.jpeg','.gif','.mp4','.f3d','.step','.stl','.npz','.pdf','.html'}
    for p in fs:
        if p.suffix.lower() in reviewed_ext and approved.get(p.relative_to(ROOT).as_posix())!=hashlib.sha256(p.read_bytes()).hexdigest():
            errors.append((p.relative_to(ROOT).as_posix(),['binary_requires_review']))
    for p in fs:
        if p.suffix=='.py':
            try:ast.parse(p.read_text(),filename=str(p.relative_to(ROOT)))
            except SyntaxError as e:errors.append((str(p.relative_to(ROOT)),['syntax_error:'+str(e.lineno)]))
    model=ROOT/'simulation/mujoco/r4.xml'
    tree=ET.parse(model)
    meshdir=tree.find('compiler').get('meshdir','')
    for x in tree.findall('.//asset/mesh'):
        f=x.get('file')
        if f and not (model.parent/meshdir/f).is_file():errors.append((f,['missing_mesh']))
    if check_manifest:
        path=ROOT/'metadata/manifest.json'
        if not path.is_file():errors.append(('manifest',['missing']))
        else:
            for entry in json.loads(path.read_text())['files']:
                p=ROOT/entry['path']
                if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:errors.append((entry['path'],['hash_mismatch']))
    print(json.dumps({'ok':not errors,'files_checked':len(fs),'issues':errors},ensure_ascii=False,indent=2))
    return not errors

if __name__=='__main__':
    if '--refresh' in sys.argv:print('manifest_files',refresh())
    raise SystemExit(0 if verify('--no-manifest' not in sys.argv) else 1)
