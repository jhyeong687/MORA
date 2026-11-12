#!/usr/bin/env python3
"""Preflight for tracked project files; no personal denylist is committed."""
import re
from pathlib import Path

TEXT_EXT={'.py','.cc','.h','.sh','.yaml','.yml','.json','.jsonl','.csv','.txt','.log','.md','.html','.sdf','.urdf','.rviz','.config','.xml','.svg','.step','.dxf','.manifest',''}
PATTERNS={
 'personal_home':re.compile(r'/(?:Users|home)/[A-Za-z0-9_.-]+/'),
 'personal_email':re.compile(r'[A-Za-z0-9._%+-]+@(?:gmail|naver|daum|icloud|outlook|hotmail)\.[A-Za-z]+',re.I),
 'private_notion_url':re.compile(r'https?://(?:app\.)?notion\.(?:com|so)/[A-Za-z0-9/?=_-]{16,}',re.I),
 'signed_download':re.compile(r'X-Amz-Signature=|X-Amz-Security-Token=|X-Goog-Signature=',re.I),
 'github_token':re.compile(r'gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{24,}'),
 'api_key':re.compile(r'\bsk-[A-Za-z0-9_-]{32,}'),
 'private_key':re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
}
FORBIDDEN_NAMES={'.env','auth.json','credentials.json','id_rsa','id_ed25519'}

def inspect_file(path,relative):
    errors=[]
    if path.is_symlink():errors.append('symlink_requires_review')
    if path.name in FORBIDDEN_NAMES or any(x in ('.ssh','.codex','.config') for x in relative.parts):
        errors.append('credential_file')
    if path.stat().st_size>=95*1024**2:errors.append('file_exceeds_repository_budget')
    if path.suffix.lower() in TEXT_EXT:
        try:text=path.read_text(encoding='utf-8')
        except UnicodeError:return errors
        if relative.as_posix()!='scripts/privacy_check.py':
            errors.extend(k for k,v in PATTERNS.items() if v.search(text))
        # Optional locally stored denylist. Values never enter reports.
        deny=Path(__file__).resolve().parents[1]/'.r4-local/privacy-denylist.txt'
        if deny.exists():
            errors.extend('local_identity_marker' for x in deny.read_text().splitlines() if x and x.lower() in text.lower())
    return sorted(set(errors))

def scan(root,paths):
    return [(p.relative_to(root).as_posix(),inspect_file(p,p.relative_to(root))) for p in paths if p.is_file() and inspect_file(p,p.relative_to(root))]
