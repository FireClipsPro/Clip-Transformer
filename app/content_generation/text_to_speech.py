from elevenlabs import generate, play, set_api_key
from moviepy.editor import AudioFileClip, vfx
import os
import logging

logging.basicConfig(level=logging.INFO)
AUDIO_SLOWDOWN_AMOUNT = 0.93

class TextToSpeech:
    def __init__(self, audio_folder):
        self.audio_folder = audio_folder
        # set_api_key("9bcf5e8c6dc670017ded90c1a37e6b6e") # alexanderliteplo@gmail.com
        set_api_key("e3fdda5cd97c9767a319acab0518e1dc") # xanderliteplo@gmail.com

    # returns: {'file_name': audio_file_name, 'length': audio_length}
    def generate_audio(self,
                       audio_file_name,
                       text,
                       voice="british_affirm_2",
                       model="eleven_monolingual_v1"):
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

        audio = generate(
            text=str(text),
            voice=str(voice),
            model=str(model)
        )

        try:
            # Save the original audio temporarily
            with open(audio_file_path, 'wb') as f:
                f.write(audio)

            
            # Load the audio and adjust its speed
            audio_clip = AudioFileClip(audio_file_path)
            
            slowed_audio = audio_clip.fx(vfx.speedx, AUDIO_SLOWDOWN_AMOUNT)
            
            # Save the slowed audio to the same file
            slowed_audio.write_audiofile(audio_file_path)

            logging.info(f"Audio file saved as {audio_file_path}")

            audio_length = slowed_audio.duration
            
            audio = {'file_name': audio_file_name,
                     'text': text,
                    'length': audio_length}

            return audio

        except Exception as e:
            print(e)

        logging.info(f"Audio file saved as {audio_file_path}")

        audio_length = slowed_audio.duration

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