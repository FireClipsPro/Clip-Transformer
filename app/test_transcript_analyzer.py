import unittest
from unittest.mock import Mock
from nltk.tokenize import word_tokenize
from text_analyzer import TranscriptAnalyzer  # Ensure you've imported the class
from configuration import directories
import json


class TestTranscriptAnalyzer(unittest.TestCase):

    def mock_openai_api_call(self, input_text):
        # Tokenize the input
        tokens = word_tokenize(input_text)

        # If tokens exceed 4096, raise an error
        if len(tokens) > 4096:
            raise ValueError("Input exceeds 4096 tokens!")

        # For this example, we'll just return a dummy response if there's no error
        return {"output": "dummy_response"}

    def setUp(self):
        # Set the OpenAI API call behavior using our mock function
        self.mock_openai_api = Mock()
        self.mock_openai_api.query.side_effect = self.mock_openai_api_call  # Replace 'some_method' with the method you'd call on the OpenAI API

        self.ANALYZER = TranscriptAnalyzer(
            video_info_folder="directories.TRANSCRIPTS_FOLDER",
            music_cat_list={'key1': 'value1', 'key2': 'value2'},
            openai_api=self.mock_openai_api
        )

    def test_initializer(self):
        self.assertEqual(self.ANALYZER.TRANSCRIPTION_INFO_FILE_PATH, "directories.TRANSCRIPTS_FOLDER")
        self.assertEqual(self.ANALYZER.CATEGORY_LIST_STRING, "key1, key2, ")

    def test_split_transcript_into_chunks(self):
        # Sample transcript
        # load the transcript from the json file
        with open(directories.TRANSCRIPTS_FOLDER + "technology.mp3.json", 'r') as f:
            transcript = json.load(f)
        # Expected chunks (This might vary based on the tokenization and provided limits)

        result_chunks = self.ANALYZER.split_transcript_into_chunks(transcript)

        for chunk in result_chunks:
            print("PRINTING CHUNK ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(chunk)

    # def test_api_throws_error_for_large_input(self):
    #     # A long string that has more than 4096 tokens
    #     long_string = "word " * 4100
    #     with self.assertRaises(ValueError):
    #         self.mock_openai_api.some_method(long_string)

if __name__ == "__main__":
    unittest.main()
 