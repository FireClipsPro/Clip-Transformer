import configuration.directories as directories
# from Transcriber import WhisperTranscriber, AudioExtractor
import unittest
import json
from text_analyzer import OpenaiApi
from clip_finder import HighlightFinder  # Replace with the actual import

class TestHighlightFinder(unittest.TestCase):
    def setUp(self):
        # self.audio_extractor = AudioExtractor(directories.FULL_POD_FOLDER,
        #                         directories.AUDIO_EXTRACTIONS_FOLDER)
        # self.transcriber = WhisperTranscriber(directories.AUDIO_EXTRACTIONS_FOLDER, 
        #                                       directories.TRANSCRIPTS_FOLDER)
        self.openai_api = OpenaiApi()
        self.highlight_finder = HighlightFinder(self.openai_api,
                                                directories.HOOKS_FOLDER,
                                                directories.CLIP_END_FOLDER)

    def test_get_highlights(self):

        # extract the json file from directories.TRANSCRIPTS_FOLDER and pass it to the highlight finder
        with open(directories.TRANSCRIPTS_FOLDER + "technology" + ".json", "r") as f:
            transcription = json.load(f)

        result = self.highlight_finder.get_highlights(video_id="technology.mp4", transcript=transcription['segments'])
        
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(result)
        
        # find the average length of the segments
        total_length = 0
        for clip in result:
            total_length += clip['end'] - clip['start']
        average_length = total_length / len(result)
        print("average_length", average_length)
        #print the first chunk of text from each clip along with the length of the clip
        for clip in result:
            print(f"start: {clip['transcript'][0]}, len: {clip['end'] - clip['start']}")
            print(f"end: {clip['transcript'][-1]}")

if __name__ == '__main__':
    unittest.main()