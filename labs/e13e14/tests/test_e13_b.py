"""E13 B-track contract tests for A-to-B report handoff and fixed MD input."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'labs/e11e12'), str(ROOT / 'labs/e8e10'),
                str(ROOT / 'labs/e11e12/vendor'), '/app']
import pipeline


class FixedReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.commit = 'a' * 40
        self.path = Path(self.tmp.name) / 'fixed-md.json'
        self.envelope = {
            'schema_version': 'e11e12-1', 'kind': 'fixed-md', 'status': 'SUCCEEDED',
            'commit': self.commit,
            'data': {'commit': self.commit, 'findings': []},
            'source_report': {'job_id': 'job-a', 'trace_id': 'trace-a',
                              'uri': 'artifact://job-a/incremental-check.json',
                              'sha256': 'b' * 64},
        }
        self.path.write_text(json.dumps(self.envelope) + '\n', encoding='utf-8')

    def sha(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def test_hash_verified_report_is_loaded_with_provenance(self):
        report = pipeline.load_fixed_report(self.path, self.sha(), self.commit)
        self.assertEqual(report['source_report']['job_id'], 'job-a')
        self.assertEqual(report['data']['commit'], self.commit)

    def test_changed_report_is_rejected(self):
        digest = self.sha()
        self.path.write_text(self.path.read_text() + '\n', encoding='utf-8')
        with self.assertRaises(pipeline.Failure) as ctx:
            pipeline.load_fixed_report(self.path, digest, self.commit)
        self.assertEqual(ctx.exception.code, 'ARTIFACT_HASH_MISMATCH')

    def test_malformed_hash_is_rejected(self):
        with self.assertRaises(pipeline.Failure) as ctx:
            pipeline.load_fixed_report(self.path, 'not-a-sha', self.commit)
        self.assertEqual(ctx.exception.code, 'INVALID_REPORT_SHA')

    def test_stale_payload_commit_is_rejected(self):
        self.envelope['data']['commit'] = 'b' * 40
        self.path.write_text(json.dumps(self.envelope) + '\n', encoding='utf-8')
        with self.assertRaises(pipeline.Failure) as ctx:
            pipeline.load_fixed_report(self.path, self.sha(), self.commit)
        self.assertEqual(ctx.exception.code, 'STALE_REPORT')


if __name__ == '__main__':
    unittest.main()
