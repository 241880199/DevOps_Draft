"""E11 personal tests: cache refresh/reuse and declaration-style patch placement."""
import tempfile
import unittest
from pathlib import Path
from lab import fixture, commit, scan, patch


class StudentE11(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name) / 'sample'

    def findings(self, report):
        return sorted((f['type'], f['target'], f['dependency']) for f in report['findings'])

    def test_body_only_commit_reuses_cached_targets(self):
        fixture(self.p)
        baseline = scan(self.p)
        (self.p / 'helper.c').write_text('int helper(void){return 0+0;}\n')
        newer = commit(self.p, 'C1 helper body only')
        report = scan(self.p, baseline)
        self.assertEqual(report['commit'], newer)
        self.assertEqual(report['reused'], ['main.o', 'helper.o'])
        self.assertEqual(report['refreshed'], [])
        self.assertEqual(self.findings(report), self.findings(baseline))

    def test_include_commit_refreshes_both_targets(self):
        fixture(self.p)
        baseline = scan(self.p)
        (self.p / 'main.c').write_text('#include "extra.h"\n' + (self.p / 'main.c').read_text())
        commit(self.p, 'C1 project include')
        report = scan(self.p, baseline)
        self.assertEqual(report['refreshed'], ['main.o', 'helper.o'])
        self.assertEqual(report['reused'], [])
        self.assertIn(['MISSING', 'main.o', 'extra.h'], report['added'])
        self.assertEqual(report['actual']['main.o'], ['config.h', 'extra.h', 'main.c'])

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


if __name__ == '__main__':
    unittest.main()
