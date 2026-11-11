"""E11 B-track personal tests: fixed MD repair and declaration-style placement."""
import tempfile
import unittest
from pathlib import Path
import pipeline
from lab import fixture, commit, scan, patch


class StudentE11B(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / 'sample'

    def findings(self, report):
        return sorted((f['type'], f['target'], f['dependency']) for f in report['findings'])

    def test_repair_adds_both_missing_and_keeps_redundant(self):
        fixture(self.p)
        (self.p / 'main.c').write_text('#include "extra.h"\n' + (self.p / 'main.c').read_text())
        commit(self.p, 'C1 project include')
        report = scan(self.p)
        self.assertEqual(self.findings(report), [
            ('MISSING', 'main.o', 'config.h'),
            ('MISSING', 'main.o', 'extra.h'),
            ('REDUNDANT', 'main.o', 'unused.h'),
        ])
        diff, edits = patch(self.p, report)
        self.assertIn('+main.o: main.c unused.h config.h extra.h', diff)
        self.assertEqual(edits, [
            {'target': 'main.o', 'dependency': 'config.h', 'style': 'direct'},
            {'target': 'main.o', 'dependency': 'extra.h', 'style': 'direct'},
        ])
        self.assertIn('unused.h', (self.p / 'Makefile').read_text())
        self.assertNotIn('config.h', (self.p / 'Makefile').read_text())

    def test_macro_style_patch_edits_the_variable(self):
        fixture(self.p, 'macro')
        report = scan(self.p)
        diff, edits = patch(self.p, report)
        self.assertIn('+DEPS = main.c unused.h config.h', diff)
        self.assertIn('-DEPS = main.c unused.h\n', diff)
        self.assertNotIn('main.o: $(DEPS) config.h', diff)
        self.assertEqual(edits, [{'target': 'main.o', 'dependency': 'config.h', 'style': 'macro'}])

    def test_mixed_style_patch_edits_the_rule(self):
        fixture(self.p, 'mixed')
        report = scan(self.p)
        diff, edits = patch(self.p, report)
        self.assertIn('+main.o: main.c $(HEADERS) config.h', diff)
        self.assertNotIn('HEADERS = unused.h config.h', diff)
        self.assertEqual(edits, [{'target': 'main.o', 'dependency': 'config.h', 'style': 'mixed'}])

    def test_stale_report_stops_patch(self):
        fixture(self.p)
        report = scan(self.p)
        report['commit'] = '0' * 40
        with self.assertRaisesRegex(ValueError, 'STALE_REPORT'):
            patch(self.p, report)

    def test_fixed_md_envelope_requires_target_commit(self):
        envelope = {'schema_version': 'e11e12-1', 'kind': 'fixed-md',
                    'commit': 'a' * 40, 'status': 'SUCCEEDED'}
        pipeline.check_envelope(envelope, 'a' * 40, 'fixed-md')
        with self.assertRaises(pipeline.Failure) as ctx:
            pipeline.check_envelope(envelope, 'b' * 40, 'fixed-md')
        self.assertEqual(ctx.exception.code, 'STALE_REPORT')


if __name__ == '__main__':
    unittest.main()
