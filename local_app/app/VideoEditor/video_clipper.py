from moviepy.editor import *
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class VideoClipper:
    def __init__(self,
                 input_folder,
                 output_folder):
        self.input_video_folder_path = input_folder
        self.output_file_path = output_folder
    
    # time strings can be in the following formats:
    # "1:11:40.5" or "1:11:40" or "1:11" or "1"
    def clip_video(self, video_name, start_time, end_time, tag=""):
        end_time_sec = 0
        start_time_sec = 0
        if isinstance(start_time, str) and isinstance(end_time, str):
            start_time = self.format_time_string(start_time)
            end_time = self.format_time_string(end_time)
            start_time_sec = 0
            for i in range(len(start_time)):
                start_time_sec += start_time[i] * (60 ** (len(start_time) - i - 1))
            end_time_sec = 0
            for i in range(len(end_time)):
                end_time_sec += end_time[i] * (60 ** (len(end_time) - i - 1))
        else:
            end_time_sec = end_time
            start_time_sec = start_time
        
        if start_time > end_time:
            logging.info(f"Start time: {start_time} is after end time: {end_time}")
            raise ValueError("Start time must be before end time")
        
        
        # if the video has already been clipped, return the clip name
        if os.path.exists(self.output_file_path + tag + video_name[:-4] + f'_{start_time}_{end_time}.mp4'):
            return {'file_name': tag + video_name[:-4] + f'_{start_time}_{end_time}.mp4',
                    'start_time_sec': start_time_sec,
                    'end_time_sec': end_time_sec,
                    'time_string': f'{start_time}_{end_time}'} 
        
        # initialize the input video path
        input_video = self.input_video_folder_path + video_name
        if not os.path.exists(input_video):
            print(f'Input video {input_video} does not exist')
            raise ValueError(f'Input video {input_video} does not exist')
        
        # initialize the output video path
        output_video = self.output_file_path + tag + video_name[:-4] + f'_{start_time}_{end_time}.mp4'
        if os.path.exists(output_video):
            os.remove(output_video)
        
        # clip the video (min, sec), in (hour, min, sec)
        video_clip = VideoFileClip(input_video)
        if end_time_sec > video_clip.duration:
            # don't do any clipping and just rename the file
            os.rename(input_video, output_video)
        else:
            video_clip = video_clip.subclip(start_time, end_time)
            video_clip.write_videofile(output_video, audio_codec='aac', threads=4, preset='ultrafast')
        
        return {'file_name': tag + video_name[:-4] + f'_{start_time}_{end_time}.mp4',
                'start_time_sec': start_time_sec,
                'end_time_sec': end_time_sec,
                'time_string': f'{start_time}_{end_time}'}

    # works for all string inputs smaller too eg "1:11" or "1"
    #given input: "1:11:40.5" output: (1, 11, 40.5)
    def format_time_string(self, time):
        parts = time.split(":")
        if len(parts) == 1:
            return (0, int(parts[0]))
        elif len(parts) == 2:
            if "." in parts[1]:
                return (int(parts[0]), float(parts[1]))
            else:
                return (int(parts[0]), int(parts[1]))
        elif len(parts) == 3:
            if "." in parts[2]:
                return (int(parts[0]), int(parts[1]), float(parts[2]))
            else:
                return (int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            raise ValueError("Invalid time format")

    def clip_song(self, song_name, start_time, end_time):
        start_time = self.format_time_string(start_time)
        end_time = self.format_time_string(end_time)

        start_time_sec = 0
        for i in range(len(start_time)):
            start_time_sec += start_time[i] * (60 ** (len(start_time) - i - 1))
        end_time_sec = 0
        for i in range(len(end_time)):
            end_time_sec += end_time[i] * (60 ** (len(end_time) - i - 1))

        # if the song has already been clipped, return the file name
        if os.path.exists(self.output_file_path + song_name[:-4] + f'_{start_time}_{end_time}.mp3'):
            return {'file_name': song_name[:-4] + f'_{start_time}_{end_time}.mp3', 'start_time_sec': start_time_sec, 'end_time_sec': end_time_sec} 

        # initialize the input song path
        input_song = self.input_video_folder_path + song_name
        if not os.path.exists(input_song):
            print(f'Input song {input_song} does not exist')
            return None

        # initialize the output song path
        output_song = self.output_file_path + song_name[:-4] + f'_{start_time}_{end_time}.mp3'
        if os.path.exists(output_song):
            os.remove(output_song)

        # clip the song (min, sec), in (hour, min, sec)
        song_clip = AudioFileClip(input_song).subclip(start_time, end_time)
        song_clip.write_audiofile(output_song)

        return {'file_name': song_name[:-4] + f'_{start_time}_{end_time}.mp3', 'start_time_sec': start_time_sec, 'end_time_sec': end_time_sec}



#Testing ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RAW_VIDEO_FILE_PATH = "../../media_storage/OutputVideos/"
# INPUT_FILE_PATH = "../../media_storage/OutputVideos/"
# clipper = VideoClipper(RAW_VIDEO_FILE_PATH, INPUT_FILE_PATH)
# # make a list of all the videos in the folder
# video_names = os.listdir(INPUT_FILE_PATH)
# # clip each video 
# for video_name in video_names:
#     if video_name[-4:] == ".mp4":
#         clipper.clip_video(video_name, "0", "59")

# clipper.clip_video("lost.mp4", "0", "59")


# input_path = "../../media_storage/video_maker/audio_input/"
# output_path = "../../media_storage/video_maker/audio_input/"
# clipper = VideoClipper(input_path, output_path)
# clipper.clip_song("Dune_Part_2.mp3", "13:47", "14:34")