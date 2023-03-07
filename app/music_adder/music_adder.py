from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import random
import os

MUSIC_CATEGORY_LIST = ['funny', 'cute', 'motivational', 'fascinating', 'conspiracy', 'angry']
MUSIC_VOLUME_FACTOR = 0.1

class MusicAdder:
    
    def __init__(self, music_file_paths, video_files_path, output_path):
        self.music_files_paths = music_file_paths
        self.video_files_path = video_files_path
        self.output_path = output_path
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
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
        
        # use moviepy to add music to video overtop of the original audio
        # do not replace the original audio just add the music overtop of it
        video_clip = VideoFileClip(self.video_files_path+ video_name)
        audio_clip = AudioFileClip(music_file_path).subclip(0, video_length)
        audio_clip = audio_clip.volumex(MUSIC_VOLUME_FACTOR)
        video_clip = video_clip.set_audio(CompositeAudioClip([video_clip.audio, audio_clip]))
        video_clip.write_videofile(self.output_path + 'with_music_' + video_name)

        
        return self.output_path + 'with_music_' + video_name
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


