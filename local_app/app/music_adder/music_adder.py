from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
import random
import os
import pyloudnorm as pyln
import numpy as np
import logging
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)

MUSIC_VOLUME_FACTOR = 0.2

class MusicAdder:
    def __init__(self,
                 music_folder,
                 input_video_folder,
                 output_video_folder,
                 music_categories):
        self.music_folder = music_folder
        self.input_video_folder = input_video_folder
        self.output_video_folder = output_video_folder
        if music_categories is None:
            music_categories = {}
        else:
            self.music_categories = music_categories.keys()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def add_music_to_video_by_category(self,
                           music_category,
                           video_name,
                           output_video_name,
                           video_length,
                           music_category_options,
                           background_music_volume):
        logging.info(f'Adding music to video {video_name}')
        music_category = music_category.lower()

        if music_category not in self.music_categories:
            # choose a random music category from the music_category_options
            music_category = random.choice(music_category_options)

        output_video_name = self.__ensure_mp4_extension(output_video_name)

        music_file_path = self.__choose_song(music_category)

        self.ensure_song_exists(music_file_path)

        video_clip = VideoFileClip(self.input_video_folder + video_name)
        video_audio_loudness = self.measure_loudness(self.input_video_folder + video_name)  # removed use_max=True

        full_audio_clip = AudioFileClip(music_file_path)
        music_loudness = self.measure_loudness(music_file_path)

        # adjust music volume to be 80% of the video's average audio volume
        volume_ratio = 0.7 * (10 ** (video_audio_loudness / 20)) / (10 ** (music_loudness / 20)) * background_music_volume

        if video_length <= full_audio_clip.duration:
            logging.info(f'Video length: {video_length} is shorter than the song')

            # Trim the music clip according to the starting point and the video length
            full_audio_clip = full_audio_clip.subclip(0, video_length)
        else:
            logging.info('Video is longer than the song')
            # If the video is longer than the song, concatenate the audio until it covers the video length
            repeats_needed = int(video_length / full_audio_clip.duration) + 1
            full_audio_clip = concatenate_audioclips([full_audio_clip] * repeats_needed)
            full_audio_clip = full_audio_clip.subclip(0, video_length)
            logging.info(f'Audio clip duration: {full_audio_clip.duration}')
            logging.info(f'Video length: {video_length}')

        # Apply the volume adjustment to the audio clip
        full_audio_clip = full_audio_clip.volumex(volume_ratio)

        # Combine the original video audio with the music audio
        video_clip = video_clip.set_audio(CompositeAudioClip([video_clip.audio, full_audio_clip]))

        # Write the video with music to the output path
        video_clip.write_videofile(self.output_video_folder + output_video_name,audio_codec='aac', codec='libx264', threads=4)

        return output_video_name
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def add_music_to(self,
                    music_file_name,
                    video_name,
                    output_video_name,
                    video_length,
                    background_music_volume):
        logging.info(f'Adding music to video {video_name}')
        
        # if the music_file_name is None, don't add music just move the video to the output folder
        if music_file_name is None:
            output_video_name = self.__ensure_mp4_extension(output_video_name)
            # if the video already exists in the output folder than we don't need to add music to it
            if os.path.exists(self.output_video_folder + output_video_name):
                logging.info(f'Video {output_video_name} already exists')
                return output_video_name
            video_clip = VideoFileClip(self.input_video_folder + video_name)
            video_clip.write_videofile(self.output_video_folder + output_video_name, audio_codec='aac', codec='libx264', threads=4)
            return output_video_name
        
        # if the video already exists in the output folder than we don't need to add music to it
        if os.path.exists(self.output_video_folder + output_video_name):
            logging.info(f'Video {output_video_name} already exists')
            return output_video_name
        
        output_video_name = self.__ensure_mp4_extension(output_video_name)
        music_file_path = self.music_folder + music_file_name
        self.ensure_song_exists(music_file_path)

        video_clip = VideoFileClip(self.input_video_folder + video_name)

        music_audio_segment = AudioSegment.from_file(music_file_path)
        normalized_music = self.normalize_audio_chunks(music_audio_segment)
        # write the normalized music to the music file path
        normalized_music.export(music_file_path, format="mp3")
        music_clip = AudioFileClip(music_file_path)
        
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
        video_clip = video_clip.set_audio(CompositeAudioClip([video_clip.audio, music_clip]))

        # Write the video with music to the output path
        video_clip.write_videofile(self.output_video_folder + output_video_name, audio_codec='aac', codec='libx264', threads=4)
        
        # mesaure the loudness of the output video
        output_video_loudness = self.measure_loudness(self.output_video_folder + output_video_name)
        logging.info(f"Output Video Loudness: {output_video_loudness} dBFS")
        return output_video_name
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # this method currently has a problem with the last segment being too short then it cannot
    # measure the loudness of the last segment
    def normalize_audio_chunks(self, audio: AudioSegment, target_loudness=-35.0):
        logging.info(f"Normalizing audio: {audio}")
        meter = pyln.Meter(audio.frame_rate)  # Initialize loudness meter

        normalized_audio_chunks = []

        # Process audio in 10-second chunks
        chunk_length_ms = 10 * 1000  # 10 seconds in milliseconds
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i+chunk_length_ms]
            
            # Ensure chunk is longer than block size required by pyloudnorm
            if len(chunk) < meter.block_size:
                logging.warning("Skipping chunk due to insufficient length for loudness measurement.")
                continue
            
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