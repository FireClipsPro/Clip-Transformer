import elevenlabs
from moviepy.editor import AudioFileClip, vfx
import os
import logging
from pydub import AudioSegment, effects

logging.basicConfig(level=logging.INFO)
# AUDIO_SLOWDOWN_AMOUNT = 0.93

class TextToSpeech:
    def __init__(self, audio_folder):
        self.audio_folder = audio_folder
        elevenlabs.set_api_key("9bcf5e8c6dc670017ded90c1a37e6b6e") # alexanderliteplo@gmail.com
        # set_api_key("e3fdda5cd97c9767a319acab0518e1dc") # xanderliteplo@gmail.com

    # returns: {'file_name': audio_file_name, 'length': audio_length}
    def generate_audio(self,
                       audio_file_name,
                       text,
                       voice):
        audio_file_path = os.path.join(self.audio_folder, audio_file_name)
        logging.info(f"Audio file path: {audio_file_path}")
        
        if os.path.exists(audio_file_path):
            logging.info(f"Audio file already exists: {audio_file_path}")
            audio_clip = AudioFileClip(audio_file_path)
            audio_length = audio_clip.duration
            audio = {'file_name': audio_file_name,
                     'text': text,
                     'length': audio_length}
            return audio
        
        audio = elevenlabs.generate(
            text=text,
            voice=elevenlabs.Voice(
                voice_id=voice,
                settings=elevenlabs.VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.0, use_speaker_boost=True)
            )
        )
        
        elevenlabs.play(audio)
        elevenlabs.save(audio, audio_file_path)
        
        raw_sound = AudioSegment.from_file(audio_file_path)
        normalized_sound = effects.normalize(raw_sound)
        
        normalized_sound.export(audio_file_path, format="mp3")
        
        audio_clip = AudioFileClip(audio_file_path)
        audio_length = audio_clip.duration

        audio = {'file_name': audio_file_name,
                 'text': text,
                 'length': audio_length}
        logging.info(f"audio: {audio}")

        return audio
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# text = "Thank you for immersing yourself in this transformative session with Molecular Manifestations. Remember, the journey to manifesting your best life is a daily commitment. For maximum effect and continued growth, make it a ritual to listen every day. If you haven't yet, click that subscribe button. By doing so, you're not only investing in yourself but also becoming a part of a thriving community, all manifesting their dreams, just like you. Whether your day is just beginning or drawing to a close, we wish you moments of peace, clarity, and purpose. May every day and night lead you closer to the life you desire and deserve. Have a wonderful day, restful night, and, above all, a truly magnificent life."

# path = "../../../text_to_video/affirmations/"

# tts = TextToSpeech(path)

# tts.generate_audio(audio_file_name="molecular.mp3",  text=text)e

raw_sound = AudioSegment.from_file("../../media_storage/video_maker/audio_input/archeaoaccoustics.mp3")
normalized_sound = effects.normalize(raw_sound)
# save the normalized audio to a file
normalized_sound.export("../../media_storage/video_maker/audio_input/archeaoaccoustics_normalized.mp3", format="mp3")
