import unittest
from scanner_v2 import classify_result, plan, scan


def item(title, url, snippet='Research internship in human-computer interaction, PhD 2027, Seattle'):
    return {'title': title, 'link': url, 'snippet': snippet}


class ScannerTests(unittest.TestCase):
    def test_fixed_company_coverage_and_request_budget(self):
        queries = plan(739876)
        self.assertEqual(len(queries), 12)
        self.assertEqual([x[0] for x in queries[:4]], ['Microsoft', 'Meta', 'Autodesk', 'Adobe'])
        self.assertEqual(sum(x[3] for x in queries), 2)
        self.assertTrue(all(x[2] for x in queries))

    def test_official_hci_internship(self):
        value = classify_result(item('Research Intern HCI 2027',
            'https://jobs.careers.microsoft.com/global/en/job/1234'))
        self.assertIsNotNone(value)
        self.assertEqual(value['company'], 'Microsoft')
        self.assertEqual(value['year'], 2027)
        self.assertEqual(value['region'], 'US')
        self.assertIsNone(value['deadline'])

    def test_no_third_party_or_algorithm(self):
        self.assertIsNone(classify_result(item('Meta Research Intern 2027',
            'https://www.facebook.com/random/jobs')))
        self.assertIsNone(classify_result(item('Foundation model algorithm intern 2027',
            'https://www.metacareers.com/jobs/1234')))
        self.assertIsNone(classify_result(item('Research Intern HCI',
            'https://www.metacareers.com/jobs/1234', '2027 is not mentioned here'.replace('2027', 'next summer'))))

    def test_history_never_mixed_with_current(self):
        old = item('Human-AI Research Intern 2026',
                   'https://www.metacareers.com/jobs/5678',
                   'Human AI research internship 2026, New York')
        new = item('Research Intern HCI 2027',
                   'https://jobs.careers.microsoft.com/global/en/job/1234')
        def search(key, query, region):
            return [old] if 'archive' in query else [new, old]
        # Historical mocks are returned for archive requests using explicit year.
        def search_by_year(key, query, region):
            return [old] if ' 2026' in query and '2027' not in query else ([new] if '2027' in query else [])
        feed, archive = scan('mock', {'jobs':[{'id':'old','source':'Web search / SerpApi; unverified'}]},
                             {'postings':[]}, day=739876, search=search_by_year)
        self.assertTrue(all(x['year'] == 2027 for x in feed['jobs']))
        self.assertTrue(all(x['year'] in (2025, 2026) for x in archive['postings']))
        self.assertFalse(any(x.get('id') == 'old' for x in feed['jobs']))
        self.assertEqual(feed['runs'][0]['requests'], 12)
        self.assertIn('Microsoft', feed['coverage'])
        self.assertIn('Meta', feed['coverage'])


if __name__ == '__main__':
    unittest.main()
