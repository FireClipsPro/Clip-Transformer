from PIL import Image, ImageFont, ImageDraw
import numpy as np
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip
import math
import logging
import matplotlib
import os
logging.basicConfig(level=logging.ERROR)

class SubtitleAdder:
    def __init__(self,
                 input_folder_path,
                 output_folder_path):
        self.input_folder_path = input_folder_path
        self.output_folder_path = output_folder_path
    
    def group_subtitles(self, subtitle_list, interval):
        interval = float(interval)

        transcript_length = float(subtitle_list[-1]['end'])
        
        logging.info(f"Sorted Subtitle List: {subtitle_list}")
        
        grouped_subtitles = [{'text': '', 'start': 0, 'end': 0}]
        current_group = {}
        group_start_time = 0
        group_end_time = interval
        
        while grouped_subtitles[-1]['end'] < subtitle_list[-1]['end']:
            last_subtitle_added = {'text': '', 'start': 0, 'end': 0}
            current_group = {'text': '', 'start': group_start_time, 'end': group_end_time}
            #problem what if group is empty
            for subtitle in subtitle_list:
                logging.info(f"Subtitle: {subtitle}")
                if subtitle['start'] >= group_start_time and subtitle['start'] <= group_end_time:
                    if current_group == {}:
                        current_group['start'] = subtitle['start']
                    
                    logging.info(f"Subtitle {subtitle} is in the group {group_start_time} to {group_end_time}")
                    
                    current_group['text'] = current_group['text'] + (subtitle['text'] + " ")
                    last_subtitle_added = subtitle
                elif subtitle['start'] > group_end_time:
                    logging.info(f"subtitle that is out of range of group reach, moving to next group.")
                    break
            
            if current_group['text'] == '':
                current_group = {}
                group_start_time = group_end_time
                group_end_time = group_start_time + interval
            else:
                current_group['end'] = last_subtitle_added['end']
                grouped_subtitles.append(current_group)
                current_group = {}
                group_start_time = last_subtitle_added['end']
                group_end_time = group_start_time + interval
                
        grouped_subtitles[-1]['end'] = transcript_length
        
        grouped_subtitles = self.split_subtitles(grouped_subtitles)
        
        logging.info(f"Grouped Subtitles: {grouped_subtitles}")
        
        return grouped_subtitles

    def split_subtitles(self, grouped_subtitles, limit=20):
        new_subtitles = []
        for subtitle in grouped_subtitles:
            if len(subtitle['text']) > limit:
                words = subtitle['text'].split()
                logging.info(f"Splitting subtitle: {subtitle}")
                
                half = len(words) // 2
                first_half_words = words[:half]
                second_half_words = words[half:]

                first_half_text = ' '.join(first_half_words)
                second_half_text = ' '.join(second_half_words)

                first_half_subtitle = {'text': first_half_text, 'start': subtitle['start'], 'end': (subtitle['start'] + subtitle['end']) / 2}
                second_half_subtitle = {'text': second_half_text, 'start': (subtitle['start'] + subtitle['end']) / 2, 'end': subtitle['end']}

                # recursively split the first and second halves if they are still too long
                new_subtitles.extend(self.split_subtitles([first_half_subtitle], limit))
                new_subtitles.extend(self.split_subtitles([second_half_subtitle], limit))
                logging.info(f"added first half: {first_half_subtitle}")
                logging.info(f"added second half: {second_half_subtitle}")
            else:
                new_subtitles.append(subtitle)
        return new_subtitles


    def create_text_image_with_outline(self, text, fontsize, text_color, outline_color, outline_width, fontname):
        font = ImageFont.truetype(fontname, fontsize)
        text_width, text_height = font.getsize(text)
        img = Image.new('RGBA', (text_width+2*outline_width, text_height+2*outline_width), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # draw outline
        for x in range(-outline_width, outline_width+1):
            for y in range(-outline_width, outline_width+1):
                draw.text((x+outline_width, y+outline_width), text, font=font, fill=outline_color)
        
        # draw text
        draw.text((outline_width, outline_width), text, font=font, fill=text_color)
        return img

    def add_subtitles_to_video(self,
                               video_file_name,
                               subtitles,
                               output_file_name,
                               fontsize,
                               fontname,
                               x_percent,
                               y_percent,
                               interval=2):
        # if video already exists don't make it again
        if os.path.exists(self.output_folder_path + output_file_name):
            return output_file_name
        
        clip = VideoFileClip(self.input_folder_path + video_file_name)
        
        clip_height = clip.h
        
        grouped_subtitles = self.group_subtitles(subtitles, interval)
        
        clips = []
        for subtitle in grouped_subtitles:
            img = self.create_text_image_with_outline(subtitle['text'], fontsize, (255, 255, 255, 255), (0, 0, 0, 255), 3, fontname)
            txt_clip = ImageClip(np.array(img)).set_duration((float(subtitle['end']) - float(subtitle['start']))).set_start(float(subtitle['start'])).set_position(lambda t: ('center', y_percent * clip_height / 100))
            clips.append(txt_clip)
            
        final = CompositeVideoClip([clip] + clips)
        final.write_videofile(self.output_folder_path + output_file_name, codec='libx264')
        
        return output_file_name

# for item in matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
#     print(item)

# print(str(group_subtitles(subtitle_list, 2)))

# add_subtitles_to_video(video_path="../../media_storage/resized_original_videos/JordanClip_(0, 0)_(0, 15)_centered.mp4",
#                        subtitles=subtitle_list,
#                        output_path="Arial Black.mp4",
#                        fontsize=80,
#                        fontname="Arial Black.ttf",
#                        x_percent=50,
#                        y_percent=50,
#                        interval=1)

#Arial Black.ttf == good for motivational or interesting
#Helvetica.ttc == good for a skinny font
#Tahoma Bold.ttf == good for motivational or interesting
#Comic Sans Bold.ttf == Cute
#papyrus.ttx == stoner