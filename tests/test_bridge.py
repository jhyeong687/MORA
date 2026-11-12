import contextlib,io,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from privacy_check import inspect_file
import export_public

class PrivacyAndExport(unittest.TestCase):
    def test_sensitive_file_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'auth.json';p.write_text('{}')
            self.assertIn('credential_file',inspect_file(p,Path('auth.json')))

    def test_personal_path_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'note.md';p.write_text('/home/'+'example-user/private.txt')
            self.assertIn('personal_home',inspect_file(p,Path('note.md')))

    def test_new_media_needs_review(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as out:
            root=Path(td);(root/'metadata').mkdir();(root/'media').mkdir()
            (root/'metadata/reviewed_binary.json').write_text('{}')
            (root/'media/new.png').write_bytes(b'unreviewed-placeholder')
            old_root,old_argv=export_public.ROOT,sys.argv
            try:
                export_public.ROOT=root
                sys.argv=['export_public.py','--target',out,'--dry-run']
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as cm:export_public.main()
                self.assertEqual(cm.exception.code,1)
            finally:export_public.ROOT,sys.argv=old_root,old_argv

if __name__=='__main__':unittest.main()
