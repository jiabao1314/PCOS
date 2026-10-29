#!/usr/bin/env python3
"""Exercise transport loss/conflict boundaries without touching research files."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

spec = importlib.util.spec_from_file_location('shared', Path(__file__).with_name('shared_context.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name).resolve()
        m.ROOT, m.SHARED, m.RUNTIME = root, root / 'shared', root / 'runtime'
        self.remote = root / 'desktop'
        m.SHARED.mkdir(); self.remote.mkdir(); (root / 'config').mkdir()
        (root / 'config/shared_context.json').write_text(json.dumps({'desktop_shared_path': str(self.remote)}))
        for name in m.NAMES:
            (m.SHARED / name).write_text('baseline\n')
            (self.remote / name).write_text('baseline\n')
        header = 'name,path,code,verification,sha256,version,evidence,access,notes\n'
        (m.SHARED / 'RESULTS_INDEX.csv').write_text(header)
        (self.remote / 'RESULTS_INDEX.csv').write_text(header)
        m.sync('pull')

    def tearDown(self):
        self.temp.cleanup()

    def test_pull_then_push(self):
        (self.remote / m.NAMES[0]).write_text('ChatGPT decision\n')
        m.sync('pull')
        self.assertEqual((m.SHARED / m.NAMES[0]).read_text(), 'ChatGPT decision\n')
        (m.SHARED / m.NAMES[1]).write_text('Codex result\n')
        m.sync('push')
        self.assertEqual((self.remote / m.NAMES[1]).read_text(), 'Codex result\n')

    def test_conflict_is_preflight_no_partial_write(self):
        (m.SHARED / m.NAMES[0]).write_text('local edit\n')
        (m.SHARED / m.NAMES[-1]).write_text('local conflict\n')
        (self.remote / m.NAMES[-1]).write_text('remote conflict\n')
        with self.assertRaises(RuntimeError):
            m.sync('push')
        self.assertEqual((self.remote / m.NAMES[0]).read_text(), 'baseline\n')

    def test_never_propagate_deletion(self):
        (m.SHARED / m.NAMES[0]).unlink()
        with self.assertRaises(RuntimeError):
            m.sync('push')
        self.assertTrue((self.remote / m.NAMES[0]).exists())

    def test_no_baseline_refuses_different_existing_copies(self):
        (m.RUNTIME / 'baseline.json').unlink()
        (m.SHARED / m.NAMES[0]).write_text('divergent\n')
        with self.assertRaises(RuntimeError):
            m.sync('push')

    def run_fixture(self, verify, run_id):
        (m.ROOT / 'input.csv').write_text('x\n1\n')
        (m.ROOT / 'analysis.py').write_text("from pathlib import Path\nPath('new.csv').write_text('x\\n2\\n')\n")
        spec = {'id': run_id, 'task': 'fixture output', 'public_metadata_reviewed': True,
                'command': [sys.executable, 'analysis.py'], 'inputs': ['input.csv'],
                'code': ['analysis.py'], 'outputs': ['new.csv'], 'next_actions': 'Review fixture',
                'verify_commands': verify}
        path = m.ROOT / 'spec.json'
        path.write_text(json.dumps(spec))
        with patch.object(m.subprocess, 'check_output', side_effect=['f' * 40, '']):
            result = m.run(path)
        return result, json.loads((m.RUNTIME / 'runs' / (run_id + '.json')).read_text())

    def test_verified_runner_records_actual_hashes_and_keeps_sync_pending(self):
        command = [sys.executable, '-c', "from pathlib import Path; assert Path('new.csv').read_text() == 'x\\n2\\n'"]
        result, event = self.run_fixture([command], 'verified_fixture')
        self.assertEqual(result, 0)
        self.assertEqual(event['state'], 'verified')
        self.assertEqual(event['output_sha256']['new.csv'], m.digest(m.ROOT / 'new.csv'))
        self.assertEqual(event['cloud_sync'], 'pending')
        self.assertIn('verified_fixture', (self.remote / 'CODEX_RUN_LOG.md').read_text())

    def test_runner_without_checks_cannot_claim_verified(self):
        result, event = self.run_fixture([], 'unverified_fixture')
        self.assertEqual(result, 1)
        self.assertEqual(event['state'], 'unverified')

    def test_failed_verification_cannot_claim_verified(self):
        result, event = self.run_fixture([[sys.executable, '-c', 'raise SystemExit(1)']], 'failed_fixture')
        self.assertEqual(result, 1)
        self.assertEqual(event['state'], 'failed')

if __name__ == '__main__':
    unittest.main()
