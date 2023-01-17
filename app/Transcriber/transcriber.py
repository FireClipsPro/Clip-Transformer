import google.cloud.exceptions

from storage_manager import GCStorageManager
from mutagen.mp3 import MP3
import transcriber_utils
from long_speech_to_text_convertor import LongSpeechToTextConvertor
from short_speech_to_text_convertor import ShortSpeechToTextConvertor
import os


class Transcriber:

    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../helpful-symbol-374005-f716a7246dc4.json'

    def transcribe_audio_file(self, path):
        audio = MP3(path)
        if audio.info.length < 60:
            return self.transcribe_short_audio_file(path)
        else:
            return self.transcribe_long_audio_file(path)


    def transcribe_short_audio_file(self, path):
        short_speech_to_text_convertor = ShortSpeechToTextConvertor()
        transcription = short_speech_to_text_convertor.convert_speech_to_text_with_timestamps(path)
        transcriber_utils.print_transcription(transcription)
        return transcription


    def transcribe_long_audio_file(self, path):
        storage_manager = GCStorageManager()
        long_speech_to_text_convertor = LongSpeechToTextConvertor()
        try:
            bucket = storage_manager.get_bucket(storage_manager.bucket_name)
        except google.cloud.exceptions.NotFound:
            bucket = storage_manager.create_bucket(storage_manager.bucket_name)
        finally:
            wav_path = transcriber_utils.convert_to_wav(path)
            file_uri = storage_manager.store_audio_file(bucket, wav_path)
            transcription = long_speech_to_text_convertor.convert_speech_to_text_with_timestamps(file_uri)
            storage_manager.delete_audio_file(bucket, wav_path)
            transcriber_utils.print_transcription(transcription)
            return transcription


transcriber = Transcriber()
joe_elon_tesla_mp3_clip = '../videos/JoeElonTesla.mp3'
joe_elon_tesla_absolute_path = transcriber_utils.get_absolute_path(__file__, joe_elon_tesla_mp3_clip)
joe_long_mp3_clip = '../videos/TestAudioExtraction.mp3'
joe_long_absolute_path = transcriber_utils.get_absolute_path(__file__, joe_long_mp3_clip)
# transcriber.transcribe_audio_file(joe_elon_tesla_absolute_path)
# transcriber.transcribe_audio_file(joe_long_absolute_path)