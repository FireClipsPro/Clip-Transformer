import os
from google.cloud import speech
import transcriber_utils
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../helpful-symbol-374005-f716a7246dc4.json'

long_joe_clip = '../videos/TestAudioExtraction.mp3'

class LongSpeechToTextConvertor:

    def __init__(self):
        self.client = speech.SpeechClient()

    def convert_speech_to_text_with_timestamps(self, uri):
        audio = speech.RecognitionAudio(uri=uri)
        config = speech.RecognitionConfig(
            sample_rate_hertz=44100,
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True,
            language_code='en-US',
            audio_channel_count=2
        )
        operation = self.client.long_running_recognize(config=config, audio=audio)
        print("Waiting for operation to complete...")
        response = operation.result(timeout=90)
        return response

