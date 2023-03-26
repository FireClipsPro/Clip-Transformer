from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
import random
import os
import logging
logging.basicConfig(level=logging.INFO)

MUSIC_CATEGORY_LIST = ['funny', 'cute', 'motivational', 'fascinating', 'conspiracy', 'angry']
MUSIC_VOLUME_FACTOR = 0.3

class MusicAdder:
    
    def __init__(self, music_file_paths, video_files_path, output_path):
        self.music_files_paths = music_file_paths
        self.video_files_path = video_files_path
        self.output_path = output_path
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
    def add_music_to_video2(self, music_category, video_name, video_length):
    # make sure the music category is valid
        if music_category not in MUSIC_CATEGORY_LIST:
            raise Exception('Invalid music category')

        music_folder_path = self.music_files_paths[music_category]
        # choose a random file from the music folder
        music_file_path = music_folder_path + random.choice(os.listdir(music_folder_path))
        # make sure the music file exists
        if not os.path.exists(music_file_path):
            raise Exception('Music file does not exist')

        # use moviepy to add music to video overtop of the original audio
        # do not replace the original audio just add the music overtop of it
        video_clip = VideoFileClip(self.video_files_path + video_name)
        full_audio_clip = AudioFileClip(music_file_path)

        # Calculate the midpoints of the video and the music
        video_midpoint = video_length / 2
        music_midpoint = full_audio_clip.duration / 2

        # Calculate the starting point of the music, so that the midpoints align
        music_start = max(0, music_midpoint - video_midpoint)
        
        # Trim the music clip according to the starting point and the video length
        audio_clip = full_audio_clip.subclip(music_start, music_start + video_length)
        audio_clip = audio_clip.volumex(MUSIC_VOLUME_FACTOR)
        video_clip = video_clip.set_audio(CompositeAudioClip([video_clip.audio, audio_clip]))
        video_clip.write_videofile(self.output_path + 'with_music_' + video_name)

        return self.output_path + 'with_music_' + video_name
    
    def add_music_to_video(self, music_category, video_name, video_length):
        # make sure the music category is valid
        if music_category not in MUSIC_CATEGORY_LIST:
            raise Exception('Invalid music category')

        music_folder_path = self.music_files_paths[music_category]
        #choose a random file from the music folder
        music_file_path = music_folder_path + random.choice(os.listdir(music_folder_path))
        # make sure the music file exists
        if not os.path.exists(music_file_path):
            raise Exception('Music file does not exist')

        video_clip = VideoFileClip(self.video_files_path + video_name)
        full_audio_clip = AudioFileClip(music_file_path)

        if video_length <= full_audio_clip.duration:
            logging.info('Video is shorter than the song')
            # Calculate the midpoints
            video_midpoint = video_length / 2
            music_midpoint = full_audio_clip.duration / 2

            # Set the starting point for the music
            music_start = max(0, music_midpoint - video_midpoint)

            # Trim the music clip according to the starting point and the video length
            audio_clip = full_audio_clip.subclip(music_start, music_start + video_length)
        else:
            logging.info('Video is longer than the song')
            # If the video is longer than the song, concatenate the audio until it covers the video length
            repeats_needed = int(video_length / full_audio_clip.duration) + 1
            audio_clip = concatenate_audioclips([full_audio_clip] * repeats_needed)
            audio_clip = audio_clip.subclip(0, video_length)
            logging.info(f'Audio clip duration: {audio_clip.duration}')
            logging.info(f'Video length: {video_length}')
            

        # Adjust the volume of the music
        audio_clip = audio_clip.volumex(MUSIC_VOLUME_FACTOR)

        # Combine the original video audio with the music audio
        video_clip = video_clip.set_audio(CompositeAudioClip([video_clip.audio, audio_clip]))

        # Write the video with music to the output path
        video_clip.write_videofile(self.output_path + 'with_music_' + video_name)

        return self.output_path + 'with_music_' + video_name


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tests:

# ANGRY_MUSIC_FILE_PATH = '../media_storage/songs/angry/'
# CUTE_MUSIC_FILE_PATH = '../media_storage/songs/cute/'
# FUNNY_MUSIC_FILE_PATH = '../media_storage/songs/funny/'
# MOTIVATIONAL_MUSIC_FILE_PATH = '../media_storage/songs/motivational/'
# INTRIGUING_MUSIC_FILE_PATH = '../media_storage/songs/fascinating/'
# CONSPIRACY_MUSIC_FILE_PATH = '../media_storage/songs/conspiracy/'

# MUSIC_CATEGORY_PATH_DICT = {
#     'funny': FUNNY_MUSIC_FILE_PATH,
#     'cute': CUTE_MUSIC_FILE_PATH,
#     'motivational': MOTIVATIONAL_MUSIC_FILE_PATH,
#     'fascinating': INTRIGUING_MUSIC_FILE_PATH,
#     'angry': ANGRY_MUSIC_FILE_PATH,
#     'conspiracy': CONSPIRACY_MUSIC_FILE_PATH
# }
# root = "../"
# OUTPUT_FILE_PATH = f"{root}media_storage/OutputVideos/"

# myMusicAdder = MusicAdder(music_file_paths=MUSIC_CATEGORY_PATH_DICT,
#                           video_files_path=OUTPUT_FILE_PATH,
#                           output_path=OUTPUT_FILE_PATH)
# myMusicAdder.add_music_to_video(music_category='conspiracy',
#                                         video_name="resized_palestine.mp4",
#                                         video_length=300)

