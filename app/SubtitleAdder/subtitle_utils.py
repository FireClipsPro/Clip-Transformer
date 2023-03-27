from app.Transcriber.text_timestamper import TextTimeStamper
from moviepy.editor import *
import math

def get_text_per_subtitle_length(SUBTITLE_LENGTH, transcript, fps):
    result = []
    text_time_stamper = TextTimeStamper()
    stamped_text = text_time_stamper.timestamp_chunk_of_text(transcript, SUBTITLE_LENGTH)
    size = len(stamped_text)
    for i, text_object in enumerate(stamped_text):
        if i == 0 and text_object['start_time'] != 0:
            text_per_frames_obj = {}
            text_per_frames_obj['text'] = ''
            text_per_frames_obj['start_time'] = text_object['start_time']
            text_per_frames_obj['duration'] = round(text_object['end_time'] - text_object['start_time'], 2)
            text_per_frames_obj['frames'] = math.floor(text_per_frames_obj['duration'] * fps)
            text_per_frames_obj['words'] = text_object['words']
            result.append(text_per_frames_obj)
            continue
        text_per_frames_obj = {}
        text_per_frames_obj['text'] = text_object['text']
        text_per_frames_obj['start_time'] = text_object['start_time']
        text_per_frames_obj['duration'] = round(text_object['end_time'] - text_object['start_time'], 2)
        text_per_frames_obj['frames'] = math.floor(text_per_frames_obj['duration'] * fps)
        text_per_frames_obj['words'] = text_object['words']

        result.append(text_per_frames_obj)
        if i + 1 < size:
            text_duration_btw_curr_next = abs(stamped_text[i + 1]['start_time'] - text_object['end_time'])
            if text_duration_btw_curr_next > 1:
                text_per_frames_obj = {}
                text_per_frames_obj['text'] = ''
                text_per_frames_obj['start_time'] = text_object['end_time']
                text_per_frames_obj['duration'] = round(text_duration_btw_curr_next, 2)
                text_per_frames_obj['frames'] = math.floor((text_duration_btw_curr_next - 1) * fps)
                text_per_frames_obj['words'] = text_object['words']
                result.append(text_per_frames_obj)
    return result

def configure_subtitles_to_frames(frames_per_subtitle, max_text_width, fps, param):
    subtitles = []
    for subtitle_chunk in frames_per_subtitle:
        if subtitle_chunk['text'] != '':
            text_lines = get_text_lines_per_second(subtitle_chunk, max_text_width, fps, param)
        else:
            text_lines = [create_text_obj('', subtitle_chunk['start_time'], subtitle_chunk['duration'], param['FONT_SCALE'], 0, 0)]
            text_lines[0]['frames'] = subtitle_chunk['frames']
        subtitles.extend(text_lines)
    return subtitles

def get_text_lines_per_second(subtitle_chunk, max_text_width, fps, param):
    text_lines = []
    text_words = subtitle_chunk['words']
    text_sizes = get_size_of_each_word_in_text(text_words, param)
    total_width = 0
    current_text = ''
    current_text_font_scale = param['FONT_SCALE']
    start_time = text_sizes[0]['start_time'] if len(text_sizes) > 0 else 0
    end_time = text_sizes[0]['end_time'] if len(text_sizes) > 0 else 0
    for text_size in text_sizes:
        if total_width + text_size['width'] <= max_text_width:
            if current_text == '':
                current_text = text_size['word']
            else:
                current_text = f'{current_text} {text_size["word"]}'
            total_width += text_size['width']
            end_time = text_size['end_time']
        else:
            add_text_obj_to_lines(current_text, start_time, end_time, current_text_font_scale, text_lines, param)
            current_text = text_size['word']
            total_width = text_size['width']
            start_time = text_size['start_time']
            end_time = text_size['end_time']
            if total_width > max_text_width:
                current_text_font_scale = get_font_scale_which_fits_text(text_size, max_text_width, param)
            else:
                current_text_font_scale = param['FONT_SCALE']
    add_text_obj_to_lines(current_text, start_time, end_time, current_text_font_scale, text_lines, param)
    add_duration_to_objs_in_lines(text_lines, fps * param['SUBTITLE_LENGTH'])
    return text_lines

def get_size_of_each_word_in_text(text_words, param):
    text_sizes = []
    for word_info in text_words:
        add_word_obj_to_sizes(word_info, text_sizes, param)
    return text_sizes

def add_word_obj_to_sizes(word_info, text_sizes, param):
    if word_info['word'] != '':
        text = f'{word_info["word"]} '
        text_dimensions = TextClip(text, fontsize=param['FONT_SCALE'], font=param['TEXT_FONT']).size
        text_width = text_dimensions[0]
        word_size_obj = {}
        word_size_obj['word'] = word_info['word']
        word_size_obj['width'] = text_width
        word_size_obj['start_time'] = word_info['start_time']
        word_size_obj['end_time'] = word_info['end_time']
        text_sizes.append(word_size_obj)

def get_font_scale_which_fits_text(text_size, max_text_width, param):
    font_scale_decrease_per_iter = 0.01
    i = 1
    while True:
        new_font_scale = param['FONT_SCALE'] * (1 - (i * font_scale_decrease_per_iter))
        if new_font_scale <= 0:
            break
        new_text_dimensions = TextClip(text_size['word'], fontsize=new_font_scale, font=param['TEXT_FONT']).size
        new_text_width = new_text_dimensions[0]
        if new_text_width <= max_text_width:
            return new_font_scale
        i += 1
    raise Exception('Decrease font_scale_decrease_per_iter parameter as text isn\'t fitting')

def add_duration_to_objs_in_lines(text_lines, total_frames):
    sum = 0
    total_frames_used = 0
    for line in text_lines:
        sum += line['width']
    last_line = text_lines.pop()
    for line in text_lines:
        line['frames'] = int(math.floor(total_frames * (line['width'] / sum)))
        total_frames_used += line['frames']
    last_line['frames'] = total_frames - total_frames_used
    text_lines.append(last_line)

def add_text_obj_to_lines(text, start_time, end_time, font_scale, text_lines, param):
    if text != '':
        text_new_size = TextClip(text, fontsize=font_scale, font=param['TEXT_FONT']).size
        width = text_new_size[0]
        height = text_new_size[1]
        text_obj = create_text_obj(text, start_time, end_time - start_time, font_scale, width, height)
        text_lines.append(text_obj)

def create_text_obj(text, start_time, duration, font_scale, width, height):
    text_obj = {}
    text_obj['text'] = text
    text_obj['font_scale'] = font_scale
    text_obj['width'] = width
    text_obj['height'] = height
    text_obj['start_time'] = start_time
    text_obj['duration'] = round(duration, 2)
    return text_obj

def modify_text_obj(text_obj, text, font_scale, width, height):
    text_obj['text'] = text
    text_obj['font_scale'] = font_scale
    text_obj['width'] = width
    text_obj['height'] = height

def get_video_dimensions(video_clip):
    size = video_clip.size
    return size[0], size[1]

def synchronize_durations(subtitles, param):
    for i, subtitle in enumerate(subtitles):
        if i + 1 >= len(subtitles):
            continue
        new_duration = subtitles[i + 1]['start_time'] - subtitle['start_time']
        if new_duration < param['SUBTITLE_LENGTH'] + 1:
            subtitle['duration'] = round(new_duration, 2)



