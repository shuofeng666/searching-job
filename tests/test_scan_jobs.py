import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scan_jobs import empty_feed,load_feed,run_once
class ScannerTests(unittest.TestCase):
 def sample(self):return dict(title='Research Intern HCI PhD 2027',company='Autodesk',location='Toronto',region='CA',kind='job',description='HCI design tools CAD collaboration publication 2027 PhD',url='https://example.com/research?utm_source=test',source='Google Jobs',source_date='today')
 def test_empty_feed(self):
  feed=empty_feed();self.assertEqual(feed['jobs'],[]);self.assertEqual(len(feed['targets']),30);self.assertIsNone(feed['last_scan'])
 def test_regions_and_deduplication(self):
  calls=[]
  def fake(key,region,engine,query):
   calls.append((region,engine));return [self.sample()] if region=='CA' and engine=='jobs' else []
  a=run_once('private-key',empty_feed(),search=fake,time=lambda:'2026-09-17T12:00:00Z')
  self.assertEqual(len(calls),12);self.assertEqual({r for r,e in calls},{'US','CA','SG','HK'});self.assertEqual(len(a['jobs']),1)
  b=run_once('private-key',a,search=fake,time=lambda:'2026-09-18T12:00:00Z');self.assertEqual(len(b['jobs']),1);self.assertEqual(b['runs'][0]['new_jobs'],0);self.assertNotIn('private-key',str(b))
 def test_no_key(self):
  with self.assertRaises(ValueError):run_once('',empty_feed(),search=lambda *args:[])
 def test_secret_not_logged(self):
  def fail(*args):raise RuntimeError('secret-token must not be shown')
  result=run_once('secret-token',empty_feed(),search=fail,time=lambda:'2026-09-17T12:00:00Z',budget=1)
  self.assertNotIn('secret-token',str(result));self.assertEqual(result['runs'][0]['status'],'partial')
 def test_load(self):
  with TemporaryDirectory() as root:
   f=Path(root)/'feed.json';self.assertEqual(load_feed(f)['jobs'],[]);f.write_text('{"jobs":[],"runs":[],"last_scan":null}');self.assertEqual(load_feed(f)['jobs'],[])
if __name__=='__main__':unittest.main()
