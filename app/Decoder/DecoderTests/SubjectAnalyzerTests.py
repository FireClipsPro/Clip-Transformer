# import unittest

# from google.cloud import language
# from google.cloud.language import enums
# from google.cloud.language import types

# from subject_analyzer import SubjectAnalyzer

# class TestSubjectAnalyzer(unittest.TestCase):
#     def setUp(self):
#         self.analyzer = SubjectAnalyzer()
    
#     def test_analyze(self):
#         # Test analyzing a simple sentence
#         result = self.analyzer.analyze("The quick brown fox jumps over the lazy dog.")
#         self.assertEqual(result, "quick brown fox jumps lazy dog ")
        
#         # Test analyzing a sentence with multiple entities
#         result = self.analyzer.analyze("Barack Obama was the 44th President of the United States.")
#         self.assertEqual(result, "Barack Obama 44th President United States ")
        
#         # Test analyzing an empty sentence
#         result = self.analyzer.analyze("")
#         self.assertEqual(result, "")

# if __name__ == '__main__':
#     unittest.main()

import unittest

import sys
#fix this: import

sys.path.insert(0, '../Decoder/SentenceSubjectAnalyzer.py')

from Decoder.SentenceSubjectAnalyzer import SentenceSubjectAnalyzer


class TestSubjectAnalyzer(unittest.TestCase):
    def test_analyzeNLTK(self):
        # Create a SubjectAnalyzer object
        analyzer = SentenceSubjectAnalyzer()

        # Test the analyzeNLTK method with different sentences
        self.assertEqual(analyzer.analyzeNLTK("The quick brown fox jumps over the lazy dog."), "")
        self.assertEqual(analyzer.analyzeNLTK("John Smith is a software engineer."), "John Smith ")
        self.assertEqual(analyzer.analyzeNLTK("New York City is the largest city in the United States."), "New York City ")

if __name__ == '__main__':
    unittest.main()

