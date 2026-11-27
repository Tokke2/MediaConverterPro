"""Headless regression tests for archive cleanup, updates and restart helper."""
import ast
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

source = Path(__file__).resolve().parents[1] / 'fotoverktyg.pyw'
tree = ast.parse(source.read_text(encoding='utf-8'))
def find_function(name, cls=None):
    body = tree.body if cls is None else next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls).body
    return next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == name)

namespace = dict(Path=Path, re=re, time=time, os=os, shutil=shutil, stat=stat,
                 tempfile=tempfile, LOGGER=logging.getLogger('test'))
for node in (find_function('prune_archived_logs'), find_function('install_release_files', 'ReleaseUpdateWorker')):
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)

class MaintenanceTests(unittest.TestCase):
    def test_only_old_named_archives_are_deleted(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            old = folder / 'mediaforge-2020-01-01.log'
            old_unique = folder / 'mediaforge-2020-01-01-123.log'
            recent = folder / 'mediaforge-2020-01-02.log'
            other = folder / 'mediaforge-important.log'
            for path in (old, old_unique, recent, other): path.write_text('data')
            now = time.time()
            for path in (old, old_unique, other): os.utime(path, (now - 8*86400, now - 8*86400))
            namespace['prune_archived_logs'](folder, now)
            self.assertFalse(old.exists()); self.assertFalse(old_unique.exists())
            self.assertTrue(recent.exists()); self.assertTrue(other.exists())

    def test_verified_update_removes_only_its_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); data = root / 'data'; namespace.update(APP_DIR=root, APP_DATA_DIR=data)
            (root / 'app.txt').write_bytes(b'old')
            other = data / 'Backups' / 'ReleaseUpdate' / 'old-backup'; other.mkdir(parents=True)
            namespace['install_release_files'](None, 'test', {'app.txt': b'new'}, {})
            self.assertEqual((root / 'app.txt').read_bytes(), b'new')
            self.assertEqual(list(other.parent.iterdir()), [other])

    def test_update_failure_rolls_back_original(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); namespace.update(APP_DIR=root, APP_DATA_DIR=root / 'data')
            (root / 'app.txt').write_bytes(b'old')
            real_replace = os.replace
            def corrupt_once(src, dest):
                real_replace(src, dest)
                if 'release-update-' in str(src): Path(dest).write_bytes(b'corrupt')
            with patch.object(os, 'replace', side_effect=corrupt_once):
                with self.assertRaises(OSError):
                    namespace['install_release_files'](None, 'test', {'app.txt': b'new'}, {})
            self.assertEqual((root / 'app.txt').read_bytes(), b'old')

    def test_git_update_protects_main_and_divergent_branch(self):
        run = find_function('run', 'ReleaseUpdateWorker')
        exec(compile(ast.Module(body=[run], type_ignores=[]), str(source), 'exec'), namespace)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / '.git').mkdir(); namespace.update(APP_DIR=root, UPDATE_REMOTE_URL='example')
            class Worker:
                apply_update = True
                git_executable = None
                def __init__(self, branch, fast_forward):
                    self.branch, self.fast_forward, self.commands, self.results = branch, fast_forward, [], []
                    self.result_ready = SimpleNamespace(emit=self.results.append)
                def check_worktree(self): return ('local', None)
                def latest_release_tag(self): return '0.0.2'
                def local_release_files(self): return {'app': b'old'}
                def release_files_at(self, ref): return {'app': b'new'}
                def git(self, *args, **kwargs):
                    self.commands.append(args)
                    output, code = '', 0
                    if args[0] == 'symbolic-ref': output = self.branch
                    if args[0] == 'rev-parse': output = 'remote'
                    if args[0] == 'merge-base':
                        code = 0 if args[-2:] == ('HEAD', 'FETCH_HEAD') and self.fast_forward else 1
                    return SimpleNamespace(returncode=code, stdout=output)
            with patch.object(shutil, 'which', return_value='/usr/bin/git'):
                main = Worker('main', True); namespace['run'](main)
                self.assertEqual(main.results[-1]['reason'], 'protected_branch')
                divergent = Worker('feature', False); namespace['run'](divergent)
                self.assertEqual(divergent.results[-1]['reason'], 'not_fast_forward')
                self.assertNotIn('checkout', [args[0] for args in divergent.commands])
                self.assertNotIn('merge', [args[0] for args in divergent.commands])

    def test_restart_helper_waits_for_process_exit(self):
        fn = find_function('restart_after_release_update', 'Window')
        helper = next(n.value.value for n in ast.walk(fn) if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'helper' for t in n.targets))
        compile(helper, '<restart-helper>', 'exec')
        if os.name == 'nt': self.skipTest('POSIX process timing test')
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'marker.py'
            marker = Path(folder) / 'result'
            target.write_text("from pathlib import Path\nPath(__file__).with_name('result').write_text('ok')\n")
            parent = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(.5)'])
            helper_proc = subprocess.Popen([sys.executable, '-c', helper, str(parent.pid), sys.executable, str(target)])
            time.sleep(.2); self.assertFalse(marker.exists())
            parent.wait(); helper_proc.wait(timeout=5)
            for _ in range(50):
                if marker.exists(): break
                time.sleep(.02)
            self.assertEqual(marker.read_text(), 'ok')

if __name__ == '__main__': unittest.main()
