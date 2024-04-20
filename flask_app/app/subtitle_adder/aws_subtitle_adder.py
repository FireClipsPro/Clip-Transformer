from PIL import Image, ImageFont, ImageDraw
import numpy as np
from moviepy.editor import ImageClip, CompositeVideoClip
import logging
import os

logging.basicConfig(level=logging.INFO)

class AWSSubtitleAdder:
    def __init__(self):
        logging.info("Subtitle Adder Initialized")
    
    # this method groups words together into subtitles based on them falling into a certain time interval
    def group_subtitles(self,
                        subtitle_list,
                        interval,
                        number_of_characters_per_line):
        interval = float(interval)
        
        logging.info(f"Interval: {subtitle_list}")
        
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
        
        grouped_subtitles = self.split_subtitles(grouped_subtitles, number_of_characters_per_line)
        
        logging.info(f"Grouped Subtitles: {grouped_subtitles}")
        
        return grouped_subtitles

    def split_subtitles(self, grouped_subtitles, characters_per_line):
        new_subtitles = []
        for subtitle in grouped_subtitles:
            if len(subtitle['text']) > characters_per_line:
                #if words have no spaces, don't split
                if ' ' not in subtitle['text']:
                    new_subtitles.append(subtitle)
                    continue
                
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
                new_subtitles.extend(self.split_subtitles([first_half_subtitle], characters_per_line))
                new_subtitles.extend(self.split_subtitles([second_half_subtitle], characters_per_line))
                logging.info(f"added first half: {first_half_subtitle}")
                logging.info(f"added second half: {second_half_subtitle}")
            else:
                new_subtitles.append(subtitle)
        return new_subtitles

    # I don't remember why I made this but it might be useful
    def create_text_image_with_outline1(self,
                                       text: str,
                                        fontsize: int,
                                        text_color,
                                        outline_color: tuple,
                                        outline_width: int,
                                        font_name: str) -> Image.Image:
        """
        Create an image with the given text, font, and outline.

        Parameters:
        - text (str): The text to be rendered.
        - fontsize (int): Font size.
        - text_color (tuple): RGB tuple for text color.
        - outline_color (tuple): RGB tuple for outline color.
        - outline_width (int): Width of the outline.
        - font_name (str): Path to the TTF font file.

        Returns:
        - Image.Image: An image with the rendered text and outline.
        """

        # Ensure colors have an alpha channel
        outline_color = (*outline_color, 255)
        text_color = (*text_color, 255)

        # Load font
        font = ImageFont.truetype(font_name, fontsize)

        # Calculate text size using getbbox()
        bbox = font.getbbox(text)
        text_width, text_height = bbox[2], bbox[3]

        logging.info(f"Text Width: {text_width}, Text Height: {text_height}")

        # Create a new image with enough space for text and its outline
        img = Image.new('RGBA', (text_width + 2 * outline_width, text_height + 2 * outline_width), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw the outline by offsetting the text in all directions
        for x in range(-outline_width, outline_width + 1):
            for y in range(-outline_width, outline_width + 1):
                draw.text((x + outline_width, y + outline_width), text, font=font, fill=outline_color)

        # Draw the main text
        draw.text((outline_width, outline_width), text, font=font, fill=text_color)

        return img

    def create_text_image_with_outline( self,
                                        text,
                                        fontsize,
                                        text_color,
                                        outline_color,
                                        outline_width,
                                        font_name):
        outline_color = (*outline_color, 255)
        text_color = (*text_color, 255)
        
        font_path = os.path.join('./fonts', font_name)
        
        font = ImageFont.truetype(font_path, fontsize)
        text_width, text_height = font.getsize(text)
        logging.info(f"Text Width: {text_width}, Text Height: {text_height}")
        img = Image.new('RGBA',    # Change here: Use 'RGB' instead of 'RGBA'
                        (text_width + 2 * outline_width, text_height + 2 * outline_width),
                        (0, 0, 0, 0))    # Change here: Set background to black or any other color
        draw = ImageDraw.Draw(img)

        # draw outline
        for x in range(-outline_width, outline_width+1):
            for y in range(-outline_width, outline_width+1):
                draw.text((x+outline_width, y+outline_width), text, font=font, fill=outline_color)

        # draw text
        draw.text((outline_width, outline_width), text, font=font, fill=text_color)
        return img
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def add_subtitles_to_video(self,
                               clip,
                               transcription,
                               font_size,
                               font_name,
                               outline_color,
                               outline_width,
                               font_color,
                               all_caps,
                               punctuation,
                               y_percent,
                               number_of_characters_per_line,
                               interval=2):
        # if video already exists don't make it again
        transcription = self.edit_punctuation_and_caps(transcription, all_caps, punctuation)
        
        clip_height = clip.h
        
        grouped_subtitles = self.group_subtitles(transcription, interval, number_of_characters_per_line)
        
        clips = []
        for subtitle in grouped_subtitles:
            logging.info(f"text color = {font_color}")
            img = self.create_text_image_with_outline(subtitle['text'],
                                                      font_size,
                                                      text_color=font_color,
                                                      outline_color=outline_color,
                                                      outline_width=outline_width,
                                                      font_name=font_name)
            txt_clip = ImageClip(np.array(img)).set_duration((float(subtitle['end']) - float(subtitle['start']))).set_start(float(subtitle['start'])).set_position(lambda t: ('center', y_percent * clip_height / 100))
            clips.append(txt_clip)
            
        final = CompositeVideoClip([clip] + clips)

        return final
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    def edit_punctuation_and_caps(self, transcription, all_caps, punctuation):
        #make all caps
        for word in transcription:
            # remove punctuation
            if not punctuation:
                word['text'] = word['text'].replace(".", "")
                word['text'] = word['text'].replace(",", "")
                word['text'] = word['text'].replace(";", "")
            
            if all_caps:
                word['text'] = word['text'].upper()
        return transcription
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Transcription must be of form {'text': 'a bunch of words to be displayed at same time', 'start': 0, 'end': 1}
    def add_subtitles_no_grouping(self,
                                    clip,
                                    video_file_name,
                                    transcription,
                                    output_file_name,
                                    font_size,
                                    font_name,
                                    outline_color,
                                    outline_width,
                                    font_color,
                                    all_caps,
                                    punctuation,
                                    y_percent,
                                    number_of_characters_per_line):
        # if video already exists don't make it again
        transcription = self.edit_punctuation_and_caps(transcription, all_caps, punctuation)
        
        clip_height = clip.h
        
        clips = []
        for subtitle in transcription:
            img = self.create_text_image_with_outline(subtitle['text'],
                                                      font_size,
                                                      text_color=font_color,
                                                      outline_color=outline_color,
                                                      outline_width=outline_width,
                                                      font_name=font_name)
            txt_clip = ImageClip(np.array(img)).set_duration((float(subtitle['end']) - float(subtitle['start']))).set_start(float(subtitle['start'])).set_position(lambda t: ('center', y_percent * clip_height / 100))
            clips.append(txt_clip)
            
        final = CompositeVideoClip([clip] + clips)
        final.write_videofile(self.output_folder_path + output_file_name, codec='libx264', threads=4)
        
        return output_file_name
                

# Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# for item in matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
#     print(item)

# subtitle_list = [{'text': 'THIS', 'start': 0, 'end': 1},
#                 {'text': 'IS', 'start': 1, 'end': 2},
#                 {'text': 'A', 'start': 2, 'end': 3},
#                 {'text': 'TEST TO SEE', 'start': 3, 'end': 4},
#                 {'text': 'IF THIS WORKS', 'start': 4, 'end': 5}]

# # print(str(group_subtitles(subtitle_list, 2))) 

# # video_file_name=video_with_media['file_name'],
# # transcription=transcription['word_segments'],
# # output_file_name='sub_' + video_with_media['file_name'],
# theme = {
#         "HEAD_TRACKING_ENABLED" : True,
#         "SECONDS_PER_PHOTO" : 6,
#         "PERECENT_OF_IMAGES_TO_BE_FULLSCREEN" : 0.3,
#         "MAXIMUM_PAUSE_LENGTH" : 0.5,
#         "TIME_BETWEEN_IMAGES" : 1.5,
#         "Y_PERCENT_HEIGHT_OF_SUBTITLE" : 60,
#         "SUBTITLE_DURATION" : 1,
#         "DURATION_OF_FULL_SCREEN_IMAGES" : 3,
#         "FONT" : "Times New Roman Bold Italic.ttf",
#         "FONT_OUTLINE_COLOR" : (0, 0, 0), # BLACK
#         "FONT_SIZE" : 90,
#         "NUMBER_OF_CHARACTERS_PER_LINE" : 20,
#         "FONT_COLOR" : (255,255,255), # WHITE
#         "IMAGE_BORDER_COLOR(S)" : [(255, 255, 255)], 
#         "MUSIC_CATEGORY" : ["motivational", "scary"]
#     }

# adder = SubtitleAdder("../../test_material/InputVideos/",
#                       "../../test_material/OutputVideos/")

# adder.add_subtitles_to_video(video_file_name="JordanClip_15.mp4",
#                        transcription=subtitle_list,
#                        output_file_name="test.mp4",
#                        font_size=theme['FONT_SIZE'],
#                         font_name=theme['FONT'],
#                         outline_color=theme['FONT_OUTLINE_COLOR'],
#                         font_color=theme['FONT_COLOR'],
#                         x_percent=50,
#                         y_percent=theme["Y_PERCENT_HEIGHT_OF_SUBTITLE"],
#                         number_of_characters_per_line=theme["NUMBER_OF_CHARACTERS_PER_LINE"],
#                         interval=theme["SUBTITLE_DURATION"])



# Arial Black.ttf == good for motivational or interesting
# Helvetica.ttc == good for a skinny font
# Tahoma Bold.ttf == good for motivational or interesting
# Comic Sans Bold.ttf == Cute
# papyrus.ttx == stoner
#Times New Roman Bold Italic.ttf
# GOOD COMBOS:
# 6 WIDTH + 80 FONT SIZE
# 8 WIDTH + 100 FONT SIZE