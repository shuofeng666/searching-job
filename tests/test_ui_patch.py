import unittest
from ui_patch import patch,MARKER,ARCHIVE
class UIPatchTests(unittest.TestCase):
 def test_insert_once(self):
  text='<html><nav class="tabs" aria-label="页面"><button>机会</button></nav><body></body></html>'
  updated=patch(text)
  self.assertEqual(updated.count(MARKER),1)
  self.assertEqual(updated.count(ARCHIVE),1)
  self.assertEqual(patch(updated),updated)
 def test_unknown_markup_does_not_get_overwritten(self):
  with self.assertRaises(ValueError):patch('<html></body></html>')
if __name__=='__main__':unittest.main()
