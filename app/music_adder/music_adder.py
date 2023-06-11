from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
import random
import os
import logging
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)

MUSIC_VOLUME_FACTOR = 0.2

class MusicAdder:

    def __init__(self,
                 music_file_paths,
                 video_files_path,
                 output_path,
                 music_categories):
        self.music_files_paths = music_file_paths
        self.video_files_path = video_files_path
        self.output_path = output_path
        self.music_categories = music_categories.keys()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
    def add_music_to_video(self,
                           music_category,
                           video_name,
                           output_video_name,
                           video_length,
                           music_category_options):
        logging.info(f'Adding music to video {video_name}')
        music_category = music_category.lower()

        if music_category not in self.music_categories:
            # choose a random music category from the music_category_options
            music_category = random.choice(music_category_options)

        output_video_name = self.__ensure_mp4_extension(output_video_name)

        music_file_path = self.__choose_song(music_category)

        self.ensure_song_exists(music_file_path)

        video_clip = VideoFileClip(self.video_files_path + video_name)
        video_audio_loudness = self.measure_loudness(self.video_files_path + video_name)  # removed use_max=True

        full_audio_clip = AudioFileClip(music_file_path)
        music_loudness = self.measure_loudness(music_file_path)

        # adjust music volume to be 80% of the video's average audio volume
        volume_ratio = 0.7 * (10 ** (video_audio_loudness / 20)) / (10 ** (music_loudness / 20))

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
        video_clip.write_videofile(self.output_path + output_video_name, codec='libx264')

        return output_video_name

    def __ensure_mp4_extension(self, output_video_name):
        if output_video_name[-4:] != '.mp4':
            return output_video_name + '.mp4'
        else:
            return output_video_name

    def __choose_song(self, music_category):
        music_folder_path = self.music_files_paths[music_category]
        #choose a random song from the music folder
        music_file_path = music_folder_path + random.choice(os.listdir(music_folder_path))
        logging.info(f'Chosen music file: {music_file_path}')
        return music_file_path

    def ensure_song_exists(self, music_file_path):
        if not os.path.exists(music_file_path):
            raise Exception('Music file does not exist')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def measure_loudness(self, filename):
        audio = AudioSegment.from_file(filename)
        return audio.dBFS


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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