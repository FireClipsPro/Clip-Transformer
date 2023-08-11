import configuration.directories as directories
from Transcriber import WhisperTranscriber, AudioExtractor
import unittest
from text_analyzer import OpenaiApi
from clip_finder import HighlightFinder  # Replace with the actual import

class TestHighlightFinder(unittest.TestCase):
    def setUp(self):
        self.audio_extractor = AudioExtractor(directories.FULL_POD_FOLDER,
                                directories.AUDIO_EXTRACTIONS_FOLDER)
        self.transcriber = WhisperTranscriber(directories.AUDIO_EXTRACTIONS_FOLDER, 
                                              directories.TRANSCRIPTS_FOLDER)
        self.openai_api = OpenaiApi()
        self.highlight_finder = HighlightFinder(self.transcriber, self.openai_api, 'input/path')

    def test_get_highlights(self):
        audio_file_name = self.audio_extractor.extract_mp3_from_mp4('technology.mp4')
        result = self.highlight_finder.get_highlights(audio_file_name)
        
        print(result)

if __name__ == '__main__':
    unittest.main()