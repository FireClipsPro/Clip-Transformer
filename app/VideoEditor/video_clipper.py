
# VideoClipper class:
# Given a video name, filepath of video passed into constructor, and start and end time,
# return a clip of the video put into the output folder specified in the constructor.

from moviepy.editor import *

class VideoClipper:
    def __init__(self,
                 input_video_file_path,
                 output_file_path):
        self.input_video_file_path = input_video_file_path
        self.output_file_path = output_file_path
    
     # time strings can be in the following formats:
        # "1:11:40.5" or "1:11:40" or "1:11" or "1"
    def clip_video(self, video_name, start_time, end_time):
        
        start_time = self.format_time_string(start_time)
        end_time = self.format_time_string(end_time)
        
        # initialize the input video path
        input_video = self.input_video_file_path + video_name
        if not os.path.exists(input_video):
            print(f'Input video {input_video} does not exist')
            return None
        
        # initialize the output video path
        output_video = self.output_file_path + video_name[:-4] + f'_{start_time}_{end_time}.mp4'
        if os.path.exists(output_video):
            os.remove(output_video)
        
        # clip the video (min, sec), in (hour, min, sec)
        video_clip = VideoFileClip(input_video).subclip(start_time, end_time)
        video_clip.write_videofile(output_video)
        
        return video_name[:-4] + f'_{start_time}_{end_time}.mp4'

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



#Testing ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RAW_VIDEO_FILE_PATH = "../media_storage/raw_videos/"
INPUT_FILE_PATH = "../media_storage/InputVideos/"
clipper = VideoClipper(RAW_VIDEO_FILE_PATH, INPUT_FILE_PATH)

# # clipper.clip_video("Woody.mp4", "0", "1:00")
clipper.clip_video("Woody.mp4", "0", "10")

# print(clipper.format_time_string("40"))
# print(clipper.format_time_string("11:40.5"))
# print(clipper.format_time_string("1:11:40"))


