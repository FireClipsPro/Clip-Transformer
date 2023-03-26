import os
import shutil
import subprocess

YOUTUBE_SHORT_ASPECT_RATIO = 9/16
PADDING_HEIGHT = 100

class VideoResizer:
    def __init__(self,
                 input_file_path, 
                 resized_file_path):
        self.HALF_YOUTUBE_SHORT_HEIGHT = 960
        self.YOUTUBE_SHORT_HEIGHT = 1920
        self.YOUTUBE_SHORT_WIDTH = 1080
        self.YOUTUBE_VIDEO_HEIGHT = 1080
        self.YOUTUBE_VIDEO_WIDTH = 1920
        
        self.INPUT_FILE_PATH = input_file_path
        self.OUTPUT_FILE_PATH  = resized_file_path

        print("VideoResizer created")

    def resize_mp4(self, input_file, output_file, width, height):
        
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'scale={width}:{height}',
            '-c:v', 'libx264',
            '-crf', '18',
            '-preset', 'veryfast',
            output_file
        ]
        subprocess.run(command)

    def crop_mp4(self, input_file, output_file, width, height):
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'crop={width}:{height}',
            '-c:v', 'libx264',
            '-crf', '18',
            '-preset', 'veryfast',
            output_file
        ]
        subprocess.run(command)

    def get_video_dimensions(self, input_file):
        command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=p=0',
            input_file
        ]
        output = subprocess.run(command, capture_output=True).stdout.decode('utf-8')
        print("~~~~~~~~~~~~~~~")
        print("output is: " + output)
        print("~~~~~~~~~~~~~~~")

        width, height = map(int, output.strip().split(','))

        return width, height
    
    def add_bottom_padding(self, input_file, output_file, video_width, video_height, padding_height=100):
        # add 100 pixels of black padding to the bottom of the video
        command = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'pad=width={video_width}:height={video_height + padding_height}:x=0:y=0:color=black',
            '-c:v', 'libx264',
            '-crf', '18',
            '-preset', 'veryfast',
            output_file
        ]
        subprocess.run(command)

    # make video into bottom half of bottom half of tiktok/short video
    def  resize_video(self, 
                      input_file_name, 
                      output_file_name, 
                      new_width, 
                      new_height):
        # add Self.Input_file_path to the beginning of the file name if it is not there
        if input_file_name[:len(self.INPUT_FILE_PATH)] != self.INPUT_FILE_PATH:
            input_file_name = self.INPUT_FILE_PATH + input_file_name
        # do the same for the output file
        if output_file_name[:len(self.INPUT_FILE_PATH)] != self.OUTPUT_FILE_PATH:
            output_file_path_and_name = self.OUTPUT_FILE_PATH + output_file_name

        # if the output file already exists, return the name of the file
        if os.path.exists(output_file_path_and_name):
            print("Output file already exists.")
            return output_file_name
        
        # check if that file exists
        if os.path.exists(input_file_name):
            print("Input file exists.")
        else:
            print("ERROR: Input File does not exist.")
            return
        
        #delete the output file if it exists
        if os.path.exists(output_file_path_and_name):
            os.remove(output_file_path_and_name)

        # get video dimensions
        curr_width, curr_height = self.get_video_dimensions(input_file_name)

        # if video is already correct size do nothing
        if curr_width == new_width and curr_height == new_height:
            # duplicate the file and add it to the output folder
            output_file_path = os.path.join(self.OUTPUT_FILE_PATH, output_file_name)
            shutil.copy2(input_file_name, output_file_path)
            return output_file_path
        
        #make an output file for the first resize
        temp_file = os.path.splitext(output_file_path_and_name)[0] + "_temp" + os.path.splitext(output_file_path_and_name)[1]
        
        
        #crop to the proportions of a tiktok/short video
        self.crop_mp4(input_file_name,
                        temp_file,
                        (curr_height * YOUTUBE_SHORT_ASPECT_RATIO),
                        curr_height - 100)
        
        temp_curr_width, temp_curr_height = self.get_video_dimensions(temp_file)
        # make another temp file for the second resize
        temp_file_2 = os.path.splitext(output_file_path_and_name)[0] + "_temp2" + os.path.splitext(output_file_path_and_name)[1]

        self.add_bottom_padding(temp_file,
                                temp_file_2,
                                temp_curr_width,
                                temp_curr_height,
                                100)
        
        # resize the video to be half the height of a tiktok/short video
        if curr_height != new_height:
            self.resize_mp4(temp_file_2,
                            output_file_path_and_name,
                            new_width,
                            new_height)
    
        # delete the temp files if they exist
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_file_2):
            os.remove(temp_file_2)
        
        print("Resized video " + input_file_name + " to " + output_file_path_and_name)
        
        if(output_file_name == None):
            raise Exception("Error: Video was not resized. Stopping program.")
        
        return output_file_name;
        
        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# resizer = VideoResizer()

# # # check if that file exists
# # if os.path.exists(address):
# #     print("File exists")
# # else:
# #     print("File does not exist")

# resizer.resize_video("TestClip.mp4",
#                     "ResizedTestOutput.mp4",
#                     new_width=resizer.YOUTUBE_SHORT_WIDTH,
#                     new_height=resizer.YOUTUBE_SHORT_HEIGHT)
        
# print(resizer.get_video_dimensions("../OutputVideos/ResizedTestOutput.mp4"))
# # width 1280, height 720




