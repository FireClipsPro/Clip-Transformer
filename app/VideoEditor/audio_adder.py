from moviepy.editor import VideoFileClip, AudioFileClip
from pathlib import Path
import os
import sys

current_path = Path(os.path.abspath(__file__)).resolve()
transcriber_path = os.path.join(current_path.parent.parent, 'Transcriber')
sys.path.append(transcriber_path)
os.sys.path.append('../Transcriber')
import transcriber_utils as utils

class AudioAdder:

    def __init__(self, video_files_path, audio_files_path):
        self.video_files_path = video_files_path
        self.audio_files_path = audio_files_path

    def add_audio_to_video(self, audio_file_path, video_file_path):
        video = VideoFileClip(video_file_path)
        audio = AudioFileClip(audio_file_path)
        # audio = audio.set_duration(video.duration)
        final_video = video.set_audio(audio)
        output_video_path = self.get_output_video_path(video_file_path)
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
        return output_video_path

    def get_output_video_path(self, video_file_path):
        video_file_path_obj = Path(video_file_path).resolve()
        video_file_name = f'{video_file_path_obj.stem}-final{video_file_path_obj.suffix}'
        output_video_path = os.path.join(video_file_path_obj.parent, video_file_name)
        return output_video_path

    def get_temporary_audio_path(self, audio_file_path):
        audio_file_path_obj = Path(audio_file_path).resolve()
        audio_temp_file_name = f'{audio_file_path_obj.stem}-temp.m4a'
        temp_audio_video_path = os.path.join(audio_file_path_obj.parent, audio_temp_file_name)
        return temp_audio_video_path

# audio_adder = AudioAdder()
# video_file = utils.get_absolute_path(__file__, '../videos/ResizedJoeRoganClip-out.mp4')
# audio_file = utils.get_absolute_path(__file__, '../videos/JoeRoganClip.mp3')
# audio_adder.add_audio_to_video(audio_file, video_file)


