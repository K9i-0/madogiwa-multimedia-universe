import unittest
from subtitle_layout import captions,NO_START
class CaptionTests(unittest.TestCase):
 def check_text(self,text):
  pages=captions(text,600)
  self.assertEqual(''.join(p['text'].replace('\n','') for p in pages),text)
  self.assertEqual(pages[-1]['toFrame'],600)
  for p in pages:
   self.assertNotIn(p['text'][0],NO_START)
   self.assertLessEqual(len(p['text'].splitlines()),2)
   for line in p['text'].splitlines():
    self.assertLessEqual(len(line),28);self.assertNotIn(line[0],NO_START)
  return pages
 def test_reported_exclamation_quote(self):
  p=self.check_text('でも、本人は「快適です！」。そのあと席が窓際になって、さらにビルの外のベランダへ移動するの。')
  self.assertEqual(p[0]['text'],'でも、本人は「快適です！」。')
 def test_question_quote(self):
  self.check_text('入口が「この仮面の人、何してるの？」でもいいのだな。')
 def test_nested_quote(self):
  self.check_text('「『快適です！』と言ったの？」と聞いたのだ。')
 def test_long_quote(self):
  self.check_text('「'+('長いセリフ、'*12)+'そうなの？」と聞いたのだ。')
 def test_all_dialogue(self):
  from pathlib import Path
  for line in Path(__file__).with_name('dialogue.txt').read_text().splitlines():
   if '|' in line:
    with self.subTest(line=line):self.check_text(line.split('|',2)[2])
if __name__=='__main__':unittest.main()
