import elevenlabs
from moviepy.editor import AudioFileClip, vfx
import os
import logging
import pyloudnorm as pyln
import numpy as np
from pydub import AudioSegment, effects

logging.basicConfig(level=logging.INFO)
# AUDIO_SLOWDOWN_AMOUNT = 0.93

class TextToSpeech:
    def __init__(self, 
                 audio_folder, 
                 elevenlabs_api_key_path="../../elevenlabs_key.txt"):
        self.audio_folder = audio_folder
        # read the .txt file to get the API key
        with open(elevenlabs_api_key_path, "r") as file:
            elevenlabs_api_key = file.read().strip()
        elevenlabs.set_api_key(elevenlabs_api_key)

    # returns: {'file_name': audio_file_name, 'length': audio_length}
    def generate_audio(self,
                       audio_file_name,
                       text,
                       voice):
        audio_file_path = os.path.join(self.audio_folder, audio_file_name)
        logging.info(f"Generating speech: {audio_file_path}")
        
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
        normalized_sound = self.normalize_audio_chunks(raw_sound)
        normalized_sound.export(audio_file_path, format="mp3")
        
        audio_clip = AudioFileClip(audio_file_path)
        audio_length = audio_clip.duration
        audio = {'file_name': audio_file_name,
                 'text': text,
                 'length': audio_length}
        logging.info(f"Speech generated: {audio}")

        return audio
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def normalize_audio_chunks(self, audio: AudioSegment, target_loudness=-14.0):
        logging.info(f"Normalizing audio: {audio}")
        # Load the audio file with pydub
        meter = pyln.Meter(audio.frame_rate)  # Initialize loudness meter

        normalized_audio_chunks = []

        # Process audio in 10-second chunks
        chunk_length_ms = 10 * 1000  # 10 seconds in milliseconds
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i+chunk_length_ms]
            
            # Convert PyDub segment to NumPy array
            samples = np.array(chunk.get_array_of_samples())
            if chunk.channels == 2:
                samples = np.reshape(samples, (-1, 2))
            samples_float = samples.astype(np.float32) / (2**15)
            
            # Measure the loudness of the chunk
            loudness = meter.integrated_loudness(samples_float)
            
            # Calculate the needed gain to reach the target loudness
            gain = target_loudness - loudness
            normalized_chunk = chunk.apply_gain(gain)
            
            normalized_audio_chunks.append(normalized_chunk)
        
        # Concatenate all normalized chunks
        normalized_audio = sum(normalized_audio_chunks)
        
        logging.info(f"Audio normalized: {normalized_audio}")
        return normalized_audio
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# text = "Thank you for immersing yourself in this transformative session with Molecular Manifestations. Remember, the journey to manifesting your best life is a daily commitment. For maximum effect and continued growth, make it a ritual to listen every day. If you haven't yet, click that subscribe button. By doing so, you're not only investing in yourself but also becoming a part of a thriving community, all manifesting their dreams, just like you. Whether your day is just beginning or drawing to a close, we wish you moments of peace, clarity, and purpose. May every day and night lead you closer to the life you desire and deserve. Have a wonderful day, restful night, and, above all, a truly magnificent life."

# path = "../../../text_to_video/affirmations/"

# tts = TextToSpeech(path)

# tts.generate_audio(audio_file_name="molecular.mp3",  text=text)e

raw_sound = "../../media_storage/video_maker/audio_input/archeaoaccoustics.mp3"






# audio_file_path = "../../media_storage/video_maker/audio_input/archeaoaccoustics.mp3"
# normalize_audio_chunks(audio_file_path)
