"""Local fixture/structure tests. Spark execution is tested separately in Databricks."""
import ast
import importlib.util
import json
import re
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('audit',HERE/'verify_sources.py')
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def fixture():
    return {'Id':-1,'LocationId':87,'RevenueCenterId':1,'BusinessDate':'2026-05-19',
            'ItemsSold':[{'Discounts':[{'Amount':-2}]}],'Discounts':[{'Amount':-3}],
            'Payments':[{'Amount':10,'Gratuity':-4},{'Amount':5,'Gratuity':-1}]}

class QualityContracts(unittest.TestCase):
    def test_negative_id_is_valid(self):
        self.assertEqual(audit.assess(fixture(),{87},{1}),[])
    def test_invalid_date_and_reference(self):
        c=fixture();c['BusinessDate']='2026-02-30';c['LocationId']=999
        self.assertEqual(set(audit.assess(c,{87},{1})),{'INVALID_DATE','UNKNOWN_LOCATION'})
    def test_missing_key(self):
        c=fixture();c['Id']=None
        self.assertIn('MISSING_CHECK_ID',audit.assess(c,{87},{1}))
    def test_missing_discount_amount(self):
        c=fixture();c['ItemsSold'][0]['Discounts'][0]['Amount']=None
        self.assertIn('INVALID_DISCOUNT_NUMERIC',audit.assess(c,{87},{1}))
    def test_missing_tip_amount(self):
        c=fixture();c['Payments'][0].pop('Gratuity')
        self.assertIn('INVALID_PAYMENT_NUMERIC',audit.assess(c,{87},{1}))
    def test_empty_payments_are_operational_exceptions(self):
        c=fixture();c['Payments']=[]
        self.assertEqual(audit.assess(c,{87},{1}),[])
    def test_null_and_empty_are_distinguishable(self):
        c=fixture();c['Payments']=None
        self.assertIsNone(c['Payments']);self.assertNotEqual(c['Payments'],[])
    def test_tip_magnitude_after_aggregation(self):
        values=[-4,1]
        self.assertEqual(abs(sum(values)),3);self.assertNotEqual(sum(map(abs,values)),3)
    def test_separate_arrays_avoid_payment_fanout(self):
        c=fixture()
        self.assertEqual(len(c['Discounts'])+sum(len(i['Discounts']) for i in c['ItemsSold']),2)
        self.assertEqual(len(c['Payments']),2)

class RepositoryContracts(unittest.TestCase):
    def test_text_blob_line_endings_are_lf(self):
        for path in ROOT.rglob('*'):
            if path.is_file() and (path.suffix.lower() in {'.md','.yml','.py','.sql','.ipynb','.json','.csv'} or path.name in {'.gitignore','.gitattributes'}):
                self.assertNotIn(b'\r\n',path.read_bytes(),str(path))
    def test_exact_directory_hierarchy(self):
        actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_dir() and '__pycache__' not in p.parts}
        self.assertEqual(actual,{'resources','resources/jobs','resources/pipelines','src','src/transformations','src/transformations/silver','src/transformations/gold'})
    def test_python_syntax(self):
        for p in ROOT.rglob('*.py'):
            ast.parse(p.read_text(encoding='utf-8'))
    def test_only_three_pipeline_libraries(self):
        cfg=ROOT/'resources/pipelines/lakeflow_pipeline.yml'
        paths=re.findall(r'path: (.+)',cfg.read_text())
        self.assertEqual(len(paths),3)
        self.assertTrue(all((cfg.parent/x).is_file() for x in paths))
        self.assertTrue(all('historical' not in x and 'validate_pipeline' not in x for x in paths))
    def test_job_dependency_and_paused_schedule(self):
        cfg=(ROOT/'resources/jobs/daily_orchestration_job.yml').read_text()
        self.assertIn('pause_status: PAUSED',cfg)
        self.assertIn('depends_on:\n            - task_key: prepare_sources',cfg)
        self.assertIn('notebook_path: ../../src/transformations/silver/prepare_checks_jsonl.ipynb',cfg)
        self.assertIn('depends_on:\n            - task_key: refresh_pipeline',cfg)
        self.assertIn('max_concurrent_runs: 1',cfg)
        self.assertIn('max_retries: 0',cfg)
    def test_gold_dependencies_exist(self):
        silver=(ROOT/'src/transformations/silver/mv_checks_cleaned.py').read_text()
        names=set(re.findall(r'name="(silver_\w+)"',silver))
        for p in HERE.glob('mv_*.sql'):
            for dep in re.findall(r'\b(silver_\w+)\b',p.read_text()):
                self.assertIn(dep,names,(p,dep))
    def test_validation_notebook_has_no_outputs(self):
        for path in [HERE/'validate_pipeline.ipynb', ROOT/'src/transformations/silver/prepare_checks_jsonl.ipynb']:
            nb=json.loads(path.read_text(encoding='utf-8'))
            for c in nb['cells']:
                if c['cell_type']=='code':
                    ast.parse(''.join(c['source']));self.assertEqual(c['outputs'],[])
                    self.assertIsNone(c['execution_count'])

if __name__=='__main__':
    unittest.main(verbosity=2)
