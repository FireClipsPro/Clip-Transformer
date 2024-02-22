from advertisements import AdAdder
from moviepy.editor import VideoFileClip

import configuration.directories as directories

def get_video_dimensions(video_path):
    try:
        clip = VideoFileClip(video_path)
        width = clip.w
        height = clip.h
        return width, height
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    
def scale_video(video_path, target_width):
    try:
        clip = VideoFileClip(video_path)
        current_width = clip.w
        current_height = clip.h
        target_height = int((target_width / current_width) * current_height)
        
        resized_clip = clip.resize(width=target_width)
        resized_clip.write_videofile(directories.FINISHED_VIDEOS_FOLDER + "test_output.mp4",
                                     codec="libx264", threads=4)
        
        return target_width, target_height
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    
def crop_video_height(video_path, percent_to_remove):
    try:
        clip = VideoFileClip(video_path)
        current_width = clip.w
        current_height = clip.h
        height_to_remove = int(current_height * percent_to_remove)
        cropped_clip = clip.crop(y1=0, y2=current_height - height_to_remove)
        cropped_clip.write_videofile(directories.BANNER_FOLDER + "cropped_banner.mp4",
                                     codec="libx264", threads=4)
        return current_width, current_height - height_to_remove
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    
# Example usage
# video_path = directories.BANNER_FOLDER + "test_output.mp4"
# dimensions = get_video_dimensions(video_path)
# if dimensions:
#     width, height = dimensions
#     print(f"Video dimensions: {width} x {height}")

# scale_video(video_path, 1080)

ad_adder = AdAdder(photo_ad_folder=directories.PHOTO_AD_FOLDER,
                    banner_folder=directories.BANNER_FOLDER,
                    input_video_folder=directories.VIDEOS_WITH_OVERLAYED_MEDIA_PATH,
                    output_video_folder=directories.VIDEOS_WITH_BANNER_FOLDER,
                    image_folder=directories.IMAGE_FOLDER)

ad_adder.add_banner(True, "zero.mp4", "JordanClip_15.mp4", [3])