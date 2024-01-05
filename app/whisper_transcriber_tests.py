import unittest
from Transcriber import WhisperTranscriber
import json
from configuration import directories  # Assuming this is a module that contains the TRANSCRIPTS_FOLDER constant

class TestWhisperTranscriber(unittest.TestCase):

    def setUp(self):
        # Initialize the WhisperTranscriber instance
        self.transcriber = WhisperTranscriber(audio_extractions_folder=directories.AUDIO_EXTRACTIONS_FOLDER,
                                              transcripts_folder=directories.TRANSCRIPTS_FOLDER)

    def test_normalize_segments(self):
        # Load the transcript data
        transcript_file = directories.TRANSCRIPTS_FOLDER + "/The Disgusting Parts of History_0.38_106.74..json"
        with open(transcript_file, 'r') as file:
            transcript_data = json.load(file)

        # Assuming transcript_data contains 'segments' and 'word_segments' for the test
        segments = transcript_data['segments']
        word_segments = transcript_data['word_segments']

        # Call the normalize_segments method
        normalized_segments = self.transcriber.normalize_segments(segments, word_segments)

        # Here, write assertions to check if normalized_segments is as expected
        # Example (adjust according to your specific test case):
        self.assertEqual(len(normalized_segments), len(segments))
        for norm_segment, segment in zip(normalized_segments, segments):
            self.assertIsNotNone(norm_segment['start'])
            self.assertIsNotNone(norm_segment['end'])

        # ensure that all word segments are within the normalized segments
        for word_segment in word_segments:
            is_within_segment = False
            for segment in normalized_segments:
                if (word_segment['start'] >= segment['start'] and word_segment['end'] <= segment['end']):
                    is_within_segment = True
                    print(f"Word segment {word_segment} is within normalized segment {segment}")
                    break
            self.assertTrue(is_within_segment, f"Word segment {word_segment} is not within any normalized segment.")
        
        # ensure that there are no overlapping segments
        for i in range(len(normalized_segments) - 1):
            for j in range(i+1, len(normalized_segments)):
                self.assertTrue(normalized_segments[i]['end'] <= normalized_segments[j]['start'])
        
        # ensure that the word segments are not overlapping
        for i in range(len(word_segments) - 1):
            for j in range(i+1, len(word_segments)):
                self.assertTrue(word_segments[i]['end'] <= word_segments[j]['start'])

        # for each word segment, ensure that there is corresponding text in the normalized segments
        for word_segment in word_segments:
            found = False
            for segment in normalized_segments:
                if (word_segment['start'] >= segment['start'] 
                    and word_segment['end'] <= segment['end']
                    and word_segment['text'] in segment['text']):
                    found = True
            self.assertTrue(found)
            
    def test_create_mapping(self):
        # Define more complex test data
        segments = [
            {'start': 0, 'end': 5},
            {'start': 6, 'end': 10},
            {'start': 12, 'end': 15},
            {'start': 20, 'end': 25}
        ]
        word_segments = [
            {'start': 1, 'end': 3},  # Fits in the first segment
            {'start': 7, 'end': 9},  # Fits in the second segment
            {'start': 13, 'end': 14}, # Fits in the third segment
            {'start': 21, 'end': 23}, # Fits in the fourth segment
            {'start': 16, 'end': 19}, # Does not fit in any segment
            {'start': 4, 'end': 8}    # Overlaps with two segments but doesn't fit completely in any
        ]

        # Expected mapping
        expected_mapping = {
            (1, 3): {'start': 0, 'end': 5},
            (7, 9): {'start': 6, 'end': 10},
            (13, 14): {'start': 12, 'end': 15},
            (21, 23): {'start': 20, 'end': 25},
            # Note: (16, 19) and (4, 8) are not included as they don't fit entirely within any segment
        }

        # Call the method
        mapping = self.transcriber.create_mapping(segments, word_segments)

        # Assert the mapping is as expected
        self.assertEqual(mapping, expected_mapping)

        # Additional checks
        self.assertNotIn((16, 19), mapping)  # This word segment should not be in the mapping
        self.assertNotIn((4, 8), mapping)    # This word segment overlaps but doesn't fit entirely in any segment


        

if __name__ == '__main__':
    unittest.main()
