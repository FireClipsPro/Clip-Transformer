import os
from google.cloud import speech
from pydub import AudioSegment
import transcriber_utils
from pathlib import Path
from transcriber_utils import delete_file

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../helpful-symbol-374005-f716a7246dc4.json'

# Transcribe Local Media File
# File Size: < 10 mbs, length < 1 minute

class ShortSpeechToTextConvertor:

    def __init__(self):
        self.client = speech.SpeechClient()

    def convert_speech_to_text_with_timestamps(self, path):
        wav_path = transcriber_utils.convert_to_wav(path)
        with open(wav_path, 'rb') as f1:
            byte_data_wav = f1.read()

        audio_wav = speech.RecognitionAudio(content=byte_data_wav)
        config_wav = speech.RecognitionConfig(
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True,
            language_code='en-US',
            audio_channel_count=2
        )
        result = self.client.recognize(config=config_wav, audio=audio_wav)
        delete_file(wav_path)
        return result



# sample_rate_hertz=44100,