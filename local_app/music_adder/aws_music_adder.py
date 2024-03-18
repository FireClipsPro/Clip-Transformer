from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
import random
import os
import pyloudnorm as pyln
import numpy as np
import logging
import logging
import pydub
from pydub import AudioSegment
import pyloudnorm as pyln
import tempfile

logging.basicConfig(level=logging.INFO)

MUSIC_VOLUME_FACTOR = 0.2

class AWSMusicAdder:
    def __init__(self, music_categories=None):
        if music_categories is None:
            music_categories = {}
        else:
            self.music_categories = music_categories.keys()

    def add_music_to(self,
                    music: AudioFileClip,
                    video: VideoFileClip):

        music_clip = self.normalize_audio_chunks(music)
        
        video_length = video.duration
        
        if video_length <= music_clip.duration:
            logging.info(f'Video length: {video_length} is shorter than the song')

            # Trim the music clip according to the starting point and the video length
            music_clip = music_clip.subclip(0, video_length)
        else:
            logging.info('Video is longer than the song')
            # If the video is longer than the song, concatenate the audio until it covers the video length
            repeats_needed = int(video_length / music_clip.duration) + 1
            music_clip = concatenate_audioclips([music_clip] * repeats_needed)
            music_clip = music_clip.subclip(0, video_length)
            logging.info(f'Audio clip duration: {music_clip.duration}')
            logging.info(f'Video length: {video_length}')
            
        # Combine the original video audio with the music audio
        video = video.set_audio(CompositeAudioClip([video.audio, music_clip]))

        return video
    
    def audiofileclip_to_audiosegment(self, audio_clip: AudioFileClip) -> pydub.AudioSegment:
        """Converts an AudioFileClip to an AudioSegment using a temporary file."""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as tmp_file:
            audio_clip.write_audiofile(tmp_file.name, fps=44100)
            audio_segment = AudioSegment.from_wav(tmp_file.name)
        return audio_segment

    def audiosegment_to_audiofileclip(self, audio_segment: pydub.AudioSegment) -> AudioFileClip:
        """Converts an AudioSegment back to an AudioFileClip."""
        # Export AudioSegment to a temporary file
        temp_path = "temp_normalized_audio.mp3"
        audio_segment.export(temp_path, format="mp3")
        
        # Load the temporary file as an AudioFileClip
        normalized_clip = AudioFileClip(temp_path)
        return normalized_clip

    def normalize_audio_chunks(self, audio_clip: AudioFileClip, target_loudness=-24.0) -> AudioFileClip:
        logging.info("Normalizing audio.")
        audio_segment = self.audiofileclip_to_audiosegment(audio_clip)
        
        meter = pyln.Meter(44100)  # Assuming 44100 Hz sample rate for the loudness meter
        
        normalized_audio_chunks = []
        chunk_length_ms = 10 * 1000  # 10 seconds in milliseconds
        
        for i in range(0, len(audio_segment), chunk_length_ms):
            chunk = audio_segment[i:i+chunk_length_ms]
            
            if len(chunk) < meter.block_size:
                logging.warning("Skipping chunk due to insufficient length for loudness measurement.")
                continue
            
            samples = np.array(chunk.get_array_of_samples())
            if chunk.channels == 2:
                samples = np.reshape(samples, (-1, 2))
            samples_float = samples.astype(np.float32) / (2**15)
            
            loudness = meter.integrated_loudness(samples_float)
            gain = target_loudness - loudness
            normalized_chunk = chunk.apply_gain(gain)
            
            normalized_audio_chunks.append(normalized_chunk)
        
        # Use AudioSegment.silent() for generating a silent segment if no chunks are processed
        if normalized_audio_chunks:
            normalized_audio = sum(normalized_audio_chunks, AudioSegment.silent(duration=0))
        else:
            normalized_audio = AudioSegment.silent(duration=1000)  # Fallback to a silent segment if no chunks
        
        logging.info("Audio normalized.")
        
        return self.audiosegment_to_audiofileclip(normalized_audio)
    
    # def normalize_audio_chunks(self, audio: AudioSegment, target_loudness=-24.0):
    #     logging.info(f"Normalizing audio: {audio}")
    #     meter = pyln.Meter(audio.frame_rate)  # Initialize loudness meter

    #     normalized_audio_chunks = []

    #     # Process audio in 10-second chunks
    #     chunk_length_ms = 10 * 1000  # 10 seconds in milliseconds
    #     for i in range(0, len(audio), chunk_length_ms):
    #         chunk = audio[i:i+chunk_length_ms]
            
    #         # Check if chunk needs padding
    #         original_length = len(chunk)
    #         if original_length < meter.block_size:
    #             # Pad the chunk with silence to ensure it meets the minimum length requirement
    #             padding_length = meter.block_size - original_length
    #             chunk += AudioSegment.silent(duration=padding_length)
            
    #         samples = np.array(chunk.get_array_of_samples())
    #         if chunk.channels == 2:
    #             samples = np.reshape(samples, (-1, 2))
    #         samples_float = samples.astype(np.float32) / (2**15)
            
    #         loudness = meter.integrated_loudness(samples_float)
            
    #         gain = target_loudness - loudness
    #         normalized_chunk = chunk.apply_gain(gain)
            
    #         # If the chunk was padded, remove the added silence after normalization
    #         if original_length < meter.block_size:
    #             normalized_chunk = normalized_chunk[:original_length]
            
    #         normalized_audio_chunks.append(normalized_chunk)
        
    #     normalized_audio = sum(normalized_audio_chunks)
    #     logging.info(f"Audio normalized: {normalized_audio}")
    #     return normalized_audio

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __ensure_mp4_extension(self, output_video_name):
        if output_video_name[-4:] != '.mp4':
            return output_video_name + '.mp4'
        else:
            return output_video_name
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __choose_song(self, music_category):
        music_folder_path = self.music_folder[music_category]
        #choose a random song from the music folder
        music_file_path = music_folder_path + random.choice(os.listdir(music_folder_path))
        logging.info(f'Chosen music file: {music_file_path}')
        return music_file_path
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def ensure_song_exists(self, music_file_path):
        if not os.path.exists(music_file_path):
            raise Exception(f'Music file does not exist {music_file_path}')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def measure_loudness(self, audio_file_path):
        audio = AudioSegment.from_file(audio_file_path)
        return audio.max_dBFS
# Tests:
# root = "../../"

# ANGRY_MUSIC_FILE_PATH = f'{root}media_storage/songs/angry/'
# CUTE_MUSIC_FILE_PATH = f'{root}media_storage/songs/cute/'
# FUNNY_MUSIC_FILE_PATH = f'{root}media_storage/songs/funny/'
# MOTIVATIONAL_MUSIC_FILE_PATH = f'{root}media_storage/songs/motivational/'
# INTRIGUING_MUSIC_FILE_PATH = f'{root}media_storage/songs/fascinating/'
# CONSPIRACY_MUSIC_FILE_PATH = f'{root}media_storage/songs/conspiracy/'

# MUSIC_CATEGORY_PATH_DICT = {
#     'funny': FUNNY_MUSIC_FILE_PATH,
#     'cute': CUTE_MUSIC_FILE_PATH,
#     'motivational': MOTIVATIONAL_MUSIC_FILE_PATH,
#     'fascinating': INTRIGUING_MUSIC_FILE_PATH,
#     'angry': ANGRY_MUSIC_FILE_PATH,
#     'conspiracy': CONSPIRACY_MUSIC_FILE_PATH
# }
# OUTPUT_FILE_PATH = f"{root}media_storage/OutputVideos/"

# myMusicAdder = MusicAdder(music_file_paths=MUSIC_CATEGORY_PATH_DICT,
#                         video_files_path=OUTPUT_FILE_PATH,
#                         output_path=OUTPUT_FILE_PATH,
#                         music_categories=MUSIC_CATEGORY_PATH_DICT)

# myMusicAdder.add_music_to_video(music_category='fascinating',
#                                 video_name="earth.mp4",
#                                 output_video_name="eart_with_music.mp4",
#                                 video_length=51)