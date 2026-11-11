"""E12 external-report handoff tests for the personal B-track workspace."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pipeline
import server


class StudentE12(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)
        self.commit='a'*40
        self.report={
            'schema_version':'e11e12-1',
            'job_id':'job-a-source',
            'trace_id':'trace-a-source',
            'kind':'incremental-check',
            'commit':self.commit,
            'status':'SUCCEEDED',
            'data':{
                'commit':self.commit,
                'findings':[{'type':'MISSING','target':'main.o','dependency':'config.h'}],
            },
        }

    def write(self, report=None):
        path=self.folder/'incremental-check.json'
        path.write_text(json.dumps(report or self.report),encoding='utf-8')
        return path,hashlib.sha256(path.read_bytes()).hexdigest()

    def test_external_incremental_report_is_hash_and_commit_checked(self):
        path,digest=self.write()
        result=pipeline.load_incremental_report(path,digest,self.commit)
        self.assertEqual(result['job_id'],'job-a-source')
        self.assertEqual(result['data']['findings'][0]['dependency'],'config.h')

    def test_external_report_hash_mismatch_is_rejected(self):
        path,_=self.write()
        with self.assertRaises(pipeline.Failure) as caught:
            pipeline.load_incremental_report(path,'0'*64,self.commit)
        self.assertEqual(caught.exception.code,'ARTIFACT_HASH_MISMATCH')

    def test_external_report_wrong_kind_is_rejected(self):
        report=dict(self.report,kind='fixed-md')
        path,digest=self.write(report)
        with self.assertRaises(pipeline.Failure) as caught:
            pipeline.load_incremental_report(path,digest,self.commit)
        self.assertEqual(caught.exception.code,'ARTIFACT_TYPE_MISMATCH')

    def test_external_report_payload_commit_is_rejected(self):
        report=dict(self.report,data=dict(self.report['data'],commit='b'*40))
        path,digest=self.write(report)
        with self.assertRaises(pipeline.Failure) as caught:
            pipeline.load_incremental_report(path,digest,self.commit)
        self.assertEqual(caught.exception.code,'STALE_REPORT')

    def test_external_report_requires_full_sha256(self):
        path,_=self.write()
        with self.assertRaises(pipeline.Failure) as caught:
            pipeline.load_incremental_report(path,None,self.commit)
        self.assertEqual(caught.exception.code,'INVALID_REPORT_SHA')

    def test_api_accepts_external_report_only_under_data(self):
        root=self.folder/'api-root'
        data=root/'data'
        data.mkdir(parents=True)
        request={'mode':'e12','repo':str(data/'repo'),'base':'a'*40,'target':'b'*40,
                 'candidate':str(data/'candidate.Dockerfile'),
                 'incremental_report':str(data/'incremental-check.json'),
                 'incremental_report_sha256':'0'*64}
        with patch.object(server,'ROOT',root):
            store=server.Store(root/'jobs')
            try:
                with patch.object(store.pool,'submit'):
                    state=store.submit(request,'external-report')
                self.assertEqual(state['status'],'QUEUED')
                request=dict(request,incremental_report=str(self.folder/'outside.json'))
                with self.assertRaisesRegex(ValueError,'incremental_report must be under'):
                    store.submit(request,'outside-report')
            finally:
                store.pool.shutdown()


if __name__=='__main__':
    unittest.main()
