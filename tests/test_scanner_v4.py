import unittest
from scanner_v4 import classify, employer, plan, scan


def result(title, url='https://research.adobe.com/careers/internship-123', snippet='HCI design tools, PhD, San Jose, California'):
    return {'title': title, 'link': url, 'snippet': snippet}


class ResearchScannerTests(unittest.TestCase):
    def test_company_budget_and_rotation(self):
        for day in (14, 15, 16, 17, 18):
            jobs = plan(day)
            self.assertEqual(len(jobs), 12)
            self.assertEqual([j[0] for j in jobs[:4]], ['Microsoft', 'Meta', 'Autodesk', 'Adobe'])
            self.assertEqual(len({j[0] for j in jobs if not j[0].startswith('Topic:')}), 12 - 2)
            self.assertEqual(sum(bool(j[3]) for j in jobs), 2 if day % 7 == 0 else 0)

    def test_official_workday_and_standard_hosts(self):
        self.assertEqual(employer('https://autodesk.wd1.myworkdayjobs.com/en-US/Ext/job/123'), 'Autodesk')
        self.assertEqual(employer('https://www.metacareers.com/jobs/123'), 'Meta')
        self.assertIsNone(employer('https://autodesk.wd1.myworkdayjobs.com.attacker.net/job/1'))
        self.assertIsNone(employer('https://evil.example.com/?redirect=adobe.com'))

    def test_year_only_from_title(self):
        item = result('Research Intern, Human-AI 2027', snippet='HCI and CAD, 2026, Canada')
        self.assertEqual(classify(item)['year'], 2027)
        unknown = result('Research Intern, Human-AI', snippet='Summer 2027 Research HCI')
        self.assertIsNone(classify(unknown)['year'])
        multi = result('Research Intern, HCI 2026 / 2027')
        self.assertIsNone(classify(multi)['year'])

    def test_no_product_algorithm_fellowships_or_articles(self):
        for title in ('Product Design Intern 2027', 'Product Management Intern 2027',
                      'Algorithm Research Intern 2027', 'Machine Learning Engineer Intern 2027',
                      'Research Scientist Full Time 2027'):
            self.assertIsNone(classify(result(title)))
        self.assertIsNone(classify(result('Research Intern HCI 2027', 'https://research.adobe.com/news/intern-story')))
        self.assertIsNone(classify(result('HCI Research PhD Fellowship 2027')))

    def test_no_year_is_watch_only(self):
        no_year = result('Human-AI Research Intern', 'https://www.metacareers.com/jobs/12', 'HCI collaboration Summer 2027')
        confirmed_title = result('HCI Research Intern 2027', 'https://autodesk.wd1.myworkdayjobs.com/en-US/Ext/job/15', 'HCI fabrication, Toronto Canada')
        def search(key, query, region):
            return [no_year, confirmed_title]
        fresh, old = scan('mock', {'jobs':[], 'watch_leads':[], 'runs':[]}, {'postings':[]}, day=15, search=search)
        self.assertEqual(len(fresh['jobs']), 1)
        self.assertEqual(len(fresh['watch_leads']), 1)
        self.assertEqual(fresh['jobs'][0]['year'], 2027)
        self.assertFalse(fresh['jobs'][0]['open_verified'])
        self.assertEqual(fresh['watch_leads'][0]['year'], None)
        self.assertEqual(fresh['runs'][0]['requests'], 12)
        self.assertEqual(len(old['postings']), 0)
        self.assertIn('Adobe', fresh['coverage'])

    def test_old_product_garbage_removed(self):
        bad={'id':'bad','title':'Product Design Intern 2027','description':'HCI','year':2027,
             'source':'Employer-domain search result', 'company':'Roblox'}
        clean, past=scan('mock',{'jobs':[bad],'runs':[]},{'postings':[]},day=15,search=lambda *_: [])
        self.assertFalse(clean['jobs'])
        self.assertFalse(past['postings'])

    def test_partial_api_errors_remain_visible(self):
        def search(key,q,region):
            if 'Microsoft Research' in q: raise TimeoutError('mock failure')
            return []
        fresh,_=scan('mock',{'jobs':[],'runs':[]},{'postings':[]},day=15,search=search)
        self.assertEqual(fresh['runs'][0]['status'],'partial')
        self.assertEqual(fresh['coverage']['Microsoft']['error'],'TimeoutError')


if __name__ == '__main__': unittest.main()
