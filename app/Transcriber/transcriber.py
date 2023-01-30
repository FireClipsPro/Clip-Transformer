import google.cloud.exceptions

from storage_manager import GCStorageManager
from mutagen.mp3 import MP3
import transcriber_utils
from long_speech_to_text_convertor import LongSpeechToTextConvertor
from short_speech_to_text_convertor import ShortSpeechToTextConvertor
from text_timestamper import TextTimeStamper
import os


class Transcriber:

    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../helpful-symbol-374005-f716a7246dc4.json'

    def transcribe_audio_file(self, path, chunk_length):
        audio = MP3(path)
        if audio.info.length < 60:
            transcription = self.transcribe_short_audio_file(path)
        else:
            transcription = self.transcribe_long_audio_file(path)
        timestamper = TextTimeStamper()
        stamped_texts = timestamper.timestamp_chunk_of_text(transcription, chunk_length)
        transcriber_utils.print_transcription_text(stamped_texts)
        return transcription, stamped_texts


    def transcribe_short_audio_file(self, path):
        short_speech_to_text_convertor = ShortSpeechToTextConvertor()
        return short_speech_to_text_convertor.convert_speech_to_text_with_timestamps(path)


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
            return transcription


transcriber = Transcriber()
chunk_length = 6

joe_elon_tesla_mp3_clip = '../videos/JoeElonTesla.mp3'
joe_elon_tesla_absolute_path = transcriber_utils.get_absolute_path(__file__, joe_elon_tesla_mp3_clip)
#transcription, stamped_texts = transcriber.transcribe_audio_file(joe_elon_tesla_absolute_path, chunk_length)
path_to_joe_elon_tesla_mp3_clip = transcriber_utils.get_absolute_path(__file__, '../Vault/JoeElonTesla.txt')
# transcriber_utils.store_data(transcription, path_to_joe_elon_tesla_mp3_clip)
# transcription = transcriber_utils.load_transcription(path_to_joe_elon_tesla_mp3_clip)
# transcriber_utils.print_transcription(transcription)

joe_long_mp3_clip = '../videos/TestAudioExtraction.mp3'
joe_long_absolute_path = transcriber_utils.get_absolute_path(__file__, joe_long_mp3_clip)
# transcription, stamped_texts = transcriber.transcribe_audio_file(joe_long_absolute_path, chunk_length)
path_to_joe_long_absolute_path = transcriber_utils.get_absolute_path(__file__, '../Vault/JoeLong_long.txt')
# transcriber_utils.store_transcription(transcription, path_to_joe_long_absolute_path)
transcription = transcriber_utils.load_transcription(path_to_joe_long_absolute_path)
transcriber_utils.print_transcription(transcription)

mnm_rapgod_mp3_clip = '../videos/RAP-GOD-FAST.mp3'
mnm_rapgod_absolute_path = transcriber_utils.get_absolute_path(__file__, mnm_rapgod_mp3_clip)
# transcription, stamped_texts = transcriber.transcribe_audio_file(mnm_rapgod_absolute_path, chunk_length)
path_to_mnm_rapgod_absolute_path = transcriber_utils.get_absolute_path(__file__, '../Vault/RAP-GOD-FAST.txt')
# out_path = transcriber_utils.store_transcription(transcription, path_to_mnm_rapgod_absolute_path)
# transcription = transcriber_utils.load_transcription(path_to_mnm_rapgod_absolute_path)
# transcriber_utils.print_transcription(transcription)