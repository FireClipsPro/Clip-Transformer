from moviepy.editor import VideoFileClip, AudioFileClip
import os

class AudioAdder:
    def __init__(self, video_files_path, audio_files_path):
        self.video_files_path = video_files_path
        self.audio_files_path = audio_files_path
    
    def combine_video_audio(self, video_file_name, audio_file_name):
        
        print(os.getcwd())
        print("\n\n\n\n\n\n")
        print(self.video_files_path + video_file_name)
        video = VideoFileClip(self.video_files_path + video_file_name)
        audio = AudioFileClip(self.audio_files_path + audio_file_name)
        final_video = video.set_audio(audio)
        return final_video
