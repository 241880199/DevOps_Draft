import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

class StudentE8B(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_redundant_only_report_does_not_delete(self):
        r=scan(self.p)
        r['findings']=[f for f in r['findings'] if f['type']=='REDUNDANT']
        self.assertEqual(
            {(f['type'],f['target'],f['dependency']) for f in r['findings']},
            {('REDUNDANT','main.o','unused.h')})
        before=(self.p/'Makefile').read_bytes()
        diff,plan=patch(self.p,r)
        self.assertEqual(diff,'')
        self.assertEqual(plan,[])
        self.assertEqual((self.p/'Makefile').read_bytes(),before)
        self.assertIn('main.o: main.c unused.h',(self.p/'Makefile').read_text())

class StudentE9B(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p,'macro')

    def test_duplicate_missing_finding_is_applied_once(self):
        report=scan(self.p)
        missing=next(f for f in report['findings'] if f['type']=='MISSING')
        report['findings'].append(dict(missing))
        before=(self.p/'Makefile').read_bytes()
        diff,plan=patch(self.p,report)
        self.assertEqual(diff.count('+DEPS = main.c unused.h config.h'),1)
        self.assertEqual(plan,[{'target':'main.o','dependency':'config.h','style':'macro'}])
        self.assertEqual((self.p/'Makefile').read_bytes(),before)

class StudentE10B(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_build_failure_keeps_original_makefile(self):
        from lab import validate
        root=Path(self.tmp.name);p=self.p
        diff,plan=patch(p,scan(p))
        candidate=root/'candidate.patch';candidate.write_text(diff)
        before=(p/'Makefile').read_bytes()
        (p/'main.c').write_text('this is invalid C;\n')
        result=validate(p,candidate,root/'validation')
        self.assertTrue(result['checks']['patch_applies'])
        self.assertFalse(result['checks'].get('build',False))
        self.assertIn('COMMAND_FAILED',result['error'])
        self.assertFalse(result['accepted'])
        self.assertTrue(result['rollback'])
        self.assertTrue(result['source_unchanged'])
        self.assertEqual((p/'Makefile').read_bytes(),before)

    def test_builds_but_missing_dependency_rejected(self):
        from lab import validate,run
        root=Path(self.tmp.name);p=self.p
        main_before=(p/'main.c').read_text();mk_before=(p/'Makefile').read_text()
        (p/'main.c').write_text('#include "extra.h"\n'+main_before)
        (p/'Makefile').write_text(mk_before.replace('main.o: main.c unused.h','main.o: main.c unused.h config.h'))
        diff=run(['git','diff'],p)
        candidate=root/'builds-but-md.patch';candidate.write_text(diff)
        (p/'main.c').write_text(main_before);(p/'Makefile').write_text(mk_before)
        before=(p/'Makefile').read_bytes()
        result=validate(p,candidate,root/'validation2')
        self.assertEqual(result['checks'],{'patch_applies':True,'build':True,'test':True,'header_change':True,'no_missing':False})
        self.assertIsNone(result['error'])
        self.assertFalse(result['accepted'])
        self.assertTrue(result['rollback'])
        self.assertTrue(result['source_unchanged'])
        self.assertEqual((p/'Makefile').read_bytes(),before)

if __name__=='__main__':unittest.main()
