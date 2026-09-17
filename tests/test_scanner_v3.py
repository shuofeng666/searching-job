import unittest
from scanner_v3 import classify,plan,scan

def result(title,site='https://www.metacareers.com/jobs/123',snippet='HCI research collaboration in Seattle, Summer 2027'):
 return {'title':title,'link':site,'snippet':snippet}

class ScannerV3Tests(unittest.TestCase):
 def test_core_and_budget(self):
  work=plan(739876)
  self.assertEqual(len(work),12)
  self.assertEqual([x[0] for x in work[:4]],['Microsoft','Meta','Autodesk','Adobe'])
 def test_hci(self):
  job=classify(result('Research Scientist Intern, Human-Computer Interaction 2027'))
  self.assertIsNotNone(job)
  self.assertEqual(job['year'],2027)
 def test_excludes_product_algorithm_and_third_party(self):
  for title in ('Product Design Intern Summer 2027','Product Management Intern Summer 2027','Foundation Models Algorithm Research Intern 2027'):
   self.assertIsNone(classify(result(title)))
  self.assertIsNone(classify(result('Research Intern HCI 2027','https://thirdparty.example/job')))
 def test_unknown_year_not_misreported_as_current(self):
  item=result('Research Intern, Human-AI Collaboration','https://careers.adobe.com/us/en/job/AB12','HCI creative tools')
  self.assertIsNone(classify(item)['year'])
  fresh,history=scan('dummy',{'jobs':[],'runs':[]},{'postings':[]},day=739876,search=lambda *args:[item])
  self.assertEqual(fresh['jobs'],[])
  self.assertEqual(len(fresh['watch_leads']),1)
  self.assertEqual(history['postings'],[])
 def test_old_product_positions_removed(self):
  old={'id':'old','title':'Product Design Intern 2027','description':'Human interaction','year':2027,'source':'Employer-domain search result'}
  fresh,_=scan('dummy',{'jobs':[old]},{'postings':[]},day=739876,search=lambda *args:[])
  self.assertEqual(fresh['jobs'],[])
if __name__=='__main__':unittest.main()
