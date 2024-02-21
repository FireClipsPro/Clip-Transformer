import unittest
from sentence_subject_analyzer import ImageQueryCreator

class TestSentenceSubjectAnalyzer(unittest.TestCase):

    def test_process_transcription(self):
        analyzer = ImageQueryCreator()
        transcription = [
            {'text': 'Hello world', 'start': 0, 'end': 5},
            {'text': 'This is a test', 'start': 5, 'end': 10},
            {'text': 'Unit tests are important', 'start': 10, 'end': 20}
        ]
        transcription_length_sec = 20
        seconds_per_query = 5
        query_list = analyzer.process_transcription(transcription, transcription_length_sec, seconds_per_query)

        print(query_list)
        
        self.assertIsNotNone(query_list)
        self.assertIsInstance(query_list, list)
        self.assertGreater(len(query_list), 0)

    def test_assign_query_to_time_chunk(self):
        analyzer = ImageQueryCreator()
        sentence_list = ['Hello world', 'This is a test', 'Unit tests are important']
        i = 0
        query = analyzer.assign_query_to_time_chunk(sentence_list, i)
        
        self.assertIsNotNone(query)
        self.assertIsInstance(query, str)
        self.assertNotEqual(query, 'null')
        self.assertNotEqual(query, 'Null')

    def test_create_queries_for_null_time_chunks(self):
        analyzer = ImageQueryCreator()
        query_list = [
            {'query': None, 'start': 0, 'end': 5},
            {'query': 'Test query', 'start': 5, 'end': 10},
            {'query': None, 'start': 10, 'end': 20}
        ]
        processed_query_list = analyzer.create_queries_for_null_time_chunks(query_list)
        
        self.assertIsNotNone(processed_query_list)
        self.assertIsInstance(processed_query_list, list)
        self.assertEqual(len(processed_query_list), len(query_list))
        for query in processed_query_list:
            self.assertIsNotNone(query['query'])

    def test_parse_sentence_subject(self):
        analyzer = ImageQueryCreator()
        sentence = "Hello world"
        query = analyzer.parse_sentence_subject(sentence)

        self.assertIsNotNone(query)
        self.assertIsInstance(query, str)
        self.assertNotEqual(query, 'null')
        self.assertNotEqual(query, 'Null')


if __name__ == '__main__':
    unittest.main()
