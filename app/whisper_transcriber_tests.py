import unittest
from Transcriber import WhisperTranscriber
import json
from configuration import directories  # Assuming this is a module that contains the TRANSCRIPTS_FOLDER constant

class TestWhisperTranscriber(unittest.TestCase):

    def setUp(self):
        # Initialize the WhisperTranscriber instance
        self.transcriber = WhisperTranscriber(audio_extractions_folder=directories.AUDIO_EXTRACTIONS_FOLDER,
                                              transcripts_folder=directories.TRANSCRIPTS_FOLDER)
            
    def test_assign_clusters_entirely_within_segment(self):
        transcription = {
            'segments': [{'start': 0, 'end': 2, 'text': 'Hello world'}],
            'word_segments': [{'start': 0.5, 'end': 1, 'text': 'Hello'}]
        }
        expected = {
            'num_segments': 1,
            'word_segments': [{'start': 0.5, 'end': 1, 'text': 'Hello', 'segment_num': 0}],
            'segments': None
        }
        result = self.transcriber.assign_clusters(transcription)
        self.assertEqual(result, expected)

    def test_assign_clusters_overlap_start(self):
        transcription = {
            'segments': [{'start': 1, 'end': 3, 'text': 'world'}],
            'word_segments': [{'start': 0.5, 'end': 1.5, 'text': 'world'}]
        }
        expected = {
            'num_segments': 1,
            'word_segments': [{'start': 0.5, 'end': 1.5, 'text': 'world', 'segment_num': 0}],
            'segments': None
        }
        result = self.transcriber.assign_clusters(transcription)
        self.assertEqual(result, expected)

    def test_assign_clusters_overlap_end(self):
        transcription = {
            'segments': [{'start': 1, 'end': 3, 'text': 'world'}],
            'word_segments': [{'start': 2.5, 'end': 3.5, 'text': 'world'}]
        }
        expected = {
            'num_segments': 1,
            'word_segments': [{'start': 2.5, 'end': 3.5, 'text': 'world', 'segment_num': 0}],
            'segments': None
        }
        result = self.transcriber.assign_clusters(transcription)
        self.assertEqual(result, expected)

    def test_assign_clusters_no_text_match(self):
        transcription = {
            'segments': [{'start': 1, 'end': 3, 'text': 'world'}],
            'word_segments': [{'start': 0.5, 'end': 3.5, 'text': 'Hello'}]
        }
        expected = {
            'num_segments': 1,
            'word_segments': [{'start': 0.5, 'end': 3.5, 'text': 'Hello'}],  # No segment_num assigned
            'segments': None
        }
        result = self.transcriber.assign_clusters(transcription)
        self.assertNotIn('segment_num', result['word_segments'][0])
        self.assertEqual(result, expected)

    def test_assign_clusters_text_in_segment_text(self):
        transcription = {
            'segments': [{'start': 1, 'end': 3, 'text': 'world'}],
            'word_segments': [{'start': 0.5, 'end': 3.5, 'text': 'world'}]
        }
        expected = {
            'num_segments': 1,
            'word_segments': [{'start': 0.5, 'end': 3.5, 'text': 'world', 'segment_num': 0}],
            'segments': None
        }
        result = self.transcriber.assign_clusters(transcription)
        self.assertEqual(result, expected)

        

if __name__ == '__main__':
    unittest.main()
