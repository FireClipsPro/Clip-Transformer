from moviepy.editor import *
import os
from pathlib import Path

current_path = Path(os.path.abspath(__file__)).resolve()
sys.path.append(str(current_path.parent))
transcriber_path = os.path.join(current_path.parent.parent, 'Transcriber')
sys.path.append(transcriber_path)
from subtitle_utils import *

# import transcriber_utils

class SubtitleAdderMv:
    def __init__(self, input_dir_path, output_dir_path, font='Arial'):
        self.SUBTITLE_LENGTH = 1 # in seconds
        self.FONT_SIZE = 65
        self.TEXT_FONT = font
        self.TEXT_COLOUR = 'white'
        self.SUBTITLE_SIZE = 0.75
        self.LINE_SPACING = 200
        self.INPUT_DIR_PATH = input_dir_path
        self.OUTPUT_DIR_PATH = output_dir_path
        pass

    # y_percent = 0 is bottom, y_percent = 100 is top
    def subtitle_adder(self, file_name, transcript, y_percent=50, font='Arial', text_colour='white'):
        self.TEXT_FONT = font
        self.TEXT_COLOUR = text_colour
        # Load the video clip and get its dimensions
        video_clip = VideoFileClip(os.path.join(self.INPUT_DIR_PATH, file_name))
        video_width, video_height = get_video_dimensions(video_clip)

        # Compute the maximum text width and the video frame rate
        max_text_width = int(video_width * self.SUBTITLE_SIZE)
        fps = video_clip.fps

        # Configure the subtitles and synchronize their durations
        param = self.get_parameters()
        text_per_subtitle_length = get_text_per_subtitle_length(self.SUBTITLE_LENGTH, transcript, fps)
        subtitles = configure_subtitles_to_frames(text_per_subtitle_length, max_text_width, fps, param)
        synchronize_durations(subtitles, param)

        # Create the text objects and composite clips
        increment = int(video_height / self.LINE_SPACING)
        text_top = create_text_obj('', 0, 0, self.FONT_SIZE, 0, 0)
        text_bottom = create_text_obj('', 0, 0, self.FONT_SIZE, 0, 0)
        composite_clips = [video_clip]
        current_text = text_top
        for subtitle in subtitles:
            current_text = self.update_text_objs(current_text, text_top, text_bottom, subtitle, max_text_width)
            top, bottom = self.get_top_bottom_clips(subtitle,
                                                    text_top,
                                                    text_bottom,
                                                    video_width,
                                                    video_height,
                                                    increment,
                                                    y_percent)
            composite_clips += [top, bottom]

        # Create the final result and save it to a file
        result = CompositeVideoClip(composite_clips)
        output_file_name = f'{os.path.splitext(file_name)[0]}_sub.mp4'
        output_file_path = os.path.join(self.OUTPUT_DIR_PATH, output_file_name)
        result.write_videofile(output_file_path, fps=fps)

        return output_file_name
    
    def get_top_bottom_clips(self,
                             subtitle,
                             text_top,
                             text_bottom,
                             video_width,
                             video_height,
                             increment,
                             y_percent):
        # Get the start time and duration of the subtitle
        start = subtitle['start_time']
        duration = subtitle['duration']

        # Get the text for the top and bottom clips, and create the text objects
        top_text = ' ' if text_top['text'] == '' else text_top['text']
        bottom_text = ' ' if text_bottom['text'] == '' else text_bottom['text']
        top = TextClip(top_text, fontsize=text_top['font_scale'], font=self.TEXT_FONT, color=self.TEXT_COLOUR)
        bottom = TextClip(bottom_text, fontsize=text_bottom['font_scale'], font=self.TEXT_FONT, color=self.TEXT_COLOUR)

        # Calculate the base y_position using the y_percent
        y_position = int(video_height * (1 - y_percent / 100))

        # Position the top and bottom text objects
        top_x = int((video_width - top.size[0]) / 2)
        top_y = y_position if text_bottom['text'] == '' else y_position - increment
        bottom_x = int((video_width - bottom.size[0]) / 2)
        bottom_y = y_position + top.size[1] + increment
        top = top.set_position((top_x, top_y)).set_duration(duration).set_start(start)
        bottom = bottom.set_position((bottom_x, bottom_y)).set_duration(duration).set_start(start)

        # Return the top and bottom clips
        return top, bottom

    def update_text_objs(self, current_text, text_top, text_bottom, subtitle, max_text_width):
        if current_text['text'] == '':
            new_text = f'{subtitle["text"]}'
        else:
            new_text = f'{current_text["text"]} {subtitle["text"]}'
        new_text = ' ' if new_text == '' else new_text
        new_text_size = TextClip(new_text, fontsize=self.FONT_SIZE, font=self.TEXT_FONT, color=self.TEXT_COLOUR).size
        new_text_width = new_text_size[0]
        new_text_height = new_text_size[1]
        if new_text_width > max_text_width:
            if current_text == text_top:
                modify_text_obj(text_bottom, subtitle['text'], subtitle['font_scale'], subtitle['width'], subtitle['height'])
                return text_bottom
            else:
                modify_text_obj(text_top, subtitle['text'], subtitle['font_scale'], subtitle['width'], subtitle['height'])
                modify_text_obj(text_bottom, '', self.FONT_SIZE, 0, 0)
                return text_top
        else:
            if current_text == text_top:
                modify_text_obj(text_top, new_text, self.FONT_SIZE, new_text_width, new_text_height)
                return text_top
            else:
                modify_text_obj(text_bottom, new_text, self.FONT_SIZE, new_text_width, new_text_height)
                return text_bottom

    def get_parameters(self):
        param = {}
        param['SUBTITLE_LENGTH'] = self.SUBTITLE_LENGTH
        param['FONT_SCALE'] = self.FONT_SIZE
        param['TEXT_FONT'] = self.TEXT_FONT
        param['TEXT_COLOUR'] = self.TEXT_COLOUR
        param['SUBTITLE_SIZE'] = 0.6
        return param

'''
input_dir = os.path.abspath('../InputVideos')
output_dir = os.path.abspath('../OutputVideos')
subtitler = SubtitleAdderMv(input_dir, output_dir)
file_name = 'JordanClipResized.mp4_6.mp4'
transcription = transcriber_utils.load_transcription(os.path.abspath('../Vault/JordanClip_short.txt'))
transcriber_utils.print_transcription(transcription)
subtitler.subtitle_adder(file_name, transcription)
'''
