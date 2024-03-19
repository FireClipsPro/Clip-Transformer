from PIL import Image, ImageFont, ImageDraw
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip
import logging
import numpy as np

logging.basicConfig(level=logging.DEBUG)

class AWSSubtitleAdder:
    def __init__(self):
        pass

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

    def string_to_rgba(self, color_name):
        color_map = {
            "black": (0, 0, 0, 255),
            "white": (255, 255, 255, 255),
        }
        
        # Default to transparent if color_name is not found
        return color_map.get(color_name.lower(), "Invalid color name")
    
    def create_text_image_with_outline( self,
                                        text,
                                        fontsize,
                                        text_color,
                                        outline_color,
                                        outline_width,
                                        font_name):
        outline_color = self.string_to_rgba(outline_color)
        text_color = self.string_to_rgba(text_color)
        font = ImageFont.truetype(font_name, fontsize)
        text_width, text_height = font.getsize('text')
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

    def add_subtitles(self,
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
                      ):

        transcription = self.edit_punctuation_and_caps(transcription["word_segments"], all_caps, punctuation)

        clips = []
        for subtitle in transcription:
            img = self.create_text_image_with_outline(subtitle['text'],
                                                      font_size,
                                                      text_color=font_color,
                                                      outline_color=outline_color,
                                                      outline_width=outline_width,
                                                      font_name=font_name)
            clip_height = clip.h
            txt_clip = ImageClip(np.array(img)).set_duration((float(subtitle['end']) - float(subtitle['start']))).set_start(float(subtitle['start'])).set_position(lambda t: ('center', y_percent * clip_height / 100))
            clips.append(txt_clip)
            
        final = CompositeVideoClip([clip] + clips)

        return final