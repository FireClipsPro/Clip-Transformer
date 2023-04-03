from moviepy.editor import VideoFileClip, AudioFileClip
from pathlib import Path
import os
import sys

current_path = Path(os.path.abspath(__file__)).resolve()
sys.path.append(str(current_path.parent))
transcriber_path = os.path.join(current_path.parent.parent, 'Transcriber')
sys.path.append(transcriber_path)
import transcriber_utils as utils

class AudioAdder:

    def __init__(self, video_files_dir_path, audio_files_dir_path):
        self.video_files_dir_path = video_files_dir_path
        self.audio_files_dir_path = audio_files_dir_path

    def add_audio_to_video(self, video_file_name, audio_file_name):
        video_file_path = os.path.join(self.video_files_dir_path, video_file_name)
        audio_file_path = os.path.join(self.audio_files_dir_path, audio_file_name)
        video = VideoFileClip(video_file_path)
        audio = AudioFileClip(audio_file_path)
        # audio = audio.set_duration(video.duration)
        final_video = video.set_audio(audio)
        output_video_name, output_video_path = self.get_output_video_path(video_file_path)
        temp_audio_path = self.get_temporary_audio_path(audio_file_path)
        final_video.write_videofile(output_video_path,
                                    codec='libx264',
                                    audio_codec='aac',
                                    temp_audiofile=temp_audio_path,
                                    audio=True,
                                    remove_temp=True)
        video.close()
        audio.close()
        final_video.close()
        return output_video_name

    def get_output_video_path(self, video_file_path):
        video_file_path_obj = Path(video_file_path).resolve()
        video_file_name = f'{video_file_path_obj.stem}-final{video_file_path_obj.suffix}'
        output_video_path = os.path.join(video_file_path_obj.parent, video_file_name)
        return video_file_name, output_video_path

    def get_temporary_audio_path(self, audio_file_path):
        audio_file_path_obj = Path(audio_file_path).resolve()
        audio_temp_file_name = f'{audio_file_path_obj.stem}-temp.m4a'
        temp_audio_video_path = os.path.join(audio_file_path_obj.parent, audio_temp_file_name)
        return temp_audio_video_path

'''
video_file_dir = utils.get_absolute_path(__file__, '../media_storage/OutputVideos')
audio_file_dir = utils.get_absolute_path(__file__, '../media_storage/audio_extractions')
audio_adder = AudioAdder(video_file_dir, audio_file_dir)
video_file_name = 'wolves_(11, 21)_(12, 19)_sub.mp4'
audio_file_name = 'wolves_(11, 21)_(12, 19).mp3'
output_path = audio_adder.add_audio_to_video(video_file_name, audio_file_name)
print(output_path)
'''
