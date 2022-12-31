import os
import subprocess

class VideoResizer:
    def __init__(self):
        
        self.HALF_YOUTUBE_SHORT_HEIGHT = 960;
        self.YOUTUBE_SHORT_HEIGHT = 1920;
        self.YOUTUBE_SHORT_WIDTH = 1080;
        
        self.YOUTUBE_VIDEO_HEIGHT = 1080;
        self.YOUTUBE_VIDEO_WIDTH = 1920;
        
        
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

    # make video into bottom half of bottom half of tiktok/short video
    def  resize_video(self, input_file_name, output_file_name, new_width, new_height):
        # add ../videos/ to the beginning of the file name if it is not there
        if input_file_name[:8] != "../videos":
            input_file_name = "../videos/" + input_file_name
        # do the same for the output file
        if output_file_name[:8] != "../videos":
            output_file_name = "../videos/" + output_file_name
        
        # check if that file exists
        if os.path.exists(input_file_name):
            print("Input file exists.")
        else:
            print("ERROR: Input File does not exist.")
            return
        
        #delete the output file if it exists
        if os.path.exists(output_file_name):
            os.remove(output_file_name)
        
        
        curr_width, curr_height = self.get_video_dimensions(input_file_name)
        
        # if video is already correct size do nothing
        if curr_width == new_width and curr_height == new_height:
            return
        
        #make an output file for the first resize
        temp_file = os.path.splitext(output_file_name)[0] + "_temp" + os.path.splitext(output_file_name)[1]
        
        # resize the video to be half the height of a tiktok/short video
        if curr_height != new_height:
            self.resize_mp4(input_file_name,
                            temp_file,
                            curr_width,
                            new_height)
    
        # crop the sides of the video to fill the bottom half of the tiktok/short video
        if curr_width != new_width:
            self.crop_mp4(temp_file,
                          output_file_name,
                          new_width,
                          new_height)
        
        # delete the temp file if it exists
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        print("Resized video " + input_file_name + " to " + output_file_name)
        
        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

        

# tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# resizer = VideoResizer()



# address = "../videos/ElvisClip.mp4"

# # check if that file exists
# if os.path.exists(address):
#     print("File exists")
# else:
#     print("File does not exist")
# resizer.resize_video("JoeRoganClip.mp4",
#                     "ResizedTestOutput.mp4",
#                     resizer.YOUTUBE_SHORT_WIDTH,
#                     resizer.YOUTUBE_SHORT_HEIGHT / 2)




        
        