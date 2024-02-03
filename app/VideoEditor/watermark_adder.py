from moviepy.editor import VideoFileClip, ImageClip, vfx, CompositeVideoClip
import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)

class WatermarkAdder:
    def __init__(self,
                 watermark_folder,
                 input_video_folder,
                 output_video_folder,
                 presets):
        self.watermark_folder = watermark_folder
        self.input_video_folder = input_video_folder
        self.output_video_folder = output_video_folder
        self.presets = presets

    def add_watermark(self, 
                      image_file_name, 
                      video_file_name, 
                      location):
        if location == None or image_file_name == None or video_file_name == None:
            # copy the video to the output folder
            destination = os.path.join(self.output_video_folder, video_file_name)
            input_video_path = os.path.join(self.input_video_folder, video_file_name)
            shutil.copy(input_video_path, destination)

            logging.info("No location provided. Skipping Watermark.")
            return video_file_name
        
        image_path = self.watermark_folder + image_file_name
        video_path = self.input_video_folder + video_file_name
        
         # If image_file_name is None, just copy the video to the output folder
        if image_file_name is None:
            destination = os.path.join(self.output_video_folder, video_file_name)
            shutil.copy(video_path, destination)
            return video_file_name
        
        # Check if image and video exist
        if not os.path.exists(image_path) or not os.path.exists(video_path):
            raise ValueError("Either the image or video does not exist.")
        
        # Load the video and get its dimensions
        clip = VideoFileClip(video_path)
        w, h = clip.size
        
        # Make image translucent (assuming watermark is a PNG)
        watermark = ImageClip(image_path).set_opacity(0.7)
        
        watermark_height = watermark.size[1]
        video_height = clip.size[1]
        
        # Calculate the desired height (10% of the video's height)
        desired_height = 0.1 * video_height

        # If the watermark's height is greater than the desired height, scale it down
        if watermark_height > desired_height:
            # Calculate the scaling factor
            scaling_factor = desired_height / watermark_height
            # Resize the watermark
            watermark = watermark.resize(height=int(desired_height),
                                         width=int(watermark.size[0] * scaling_factor))
        
        # Adjust position according to the location preset
        if location == self.presets.bottom_vert:
            watermark = watermark.set_position(("center", 0.8*h))
        elif location == self.presets.top_vert:
            watermark = watermark.set_position(("center", 0.2*h))
        elif location == self.presets.top_right_hor:
            watermark = watermark.set_position((w - watermark.size[0], 0))
        elif location == self.presets.top_left_hor:
            watermark = watermark.set_position((0, 0))
        elif location == self.presets.bottom_right_hor:
            watermark = watermark.set_position((w - watermark.size[0], h - watermark.size[1]))
        elif location == self.presets.bottom_left_hor:
            watermark = watermark.set_position((0, h - watermark.size[1]))
        elif location == self.presets.center:
            watermark = watermark.set_position(("center", "center"))
        
        # Apply watermark
        final = CompositeVideoClip([clip, watermark.set_duration(clip.duration)])

        # Save new vid to output file
        output_file_path = os.path.join(self.output_video_folder, video_file_name)
        final.write_videofile(output_file_path, threads=4)

        # Close clips to free memory
        watermark.close()
        clip.close()

        return video_file_name
