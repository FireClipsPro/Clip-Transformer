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
            text_per_frames_obj['duration'] = SUBTITLE_LENGTH
            text_per_frames_obj['frames'] = text_object['start_time'] * fps
            result.append(text_per_frames_obj)
            continue
        text_per_frames_obj = {}
        text_per_frames_obj['text'] = text_object['text']
        text_per_frames_obj['start_time'] = text_object['start_time']
        text_per_frames_obj['duration'] = SUBTITLE_LENGTH
        text_per_frames_obj['frames'] = SUBTITLE_LENGTH * fps
        result.append(text_per_frames_obj)
        if i + 1 < size:
            text_duration_btw_curr_next = abs(stamped_text[i + 1]['start_time'] - text_object['end_time'])
            if text_duration_btw_curr_next > 1:
                text_per_frames_obj = {}
                text_per_frames_obj['text'] = ''
                text_per_frames_obj['start_time'] = text_object['end_time']
                text_per_frames_obj['duration'] = text_duration_btw_curr_next
                text_per_frames_obj['frames'] = (text_duration_btw_curr_next - 1) * fps
                result.append(text_per_frames_obj)
    return result

def configure_subtitles_to_frames(frames_per_subtitle, max_text_width, fps, param):
    subtitles = []
    for subtitle_chunk in frames_per_subtitle:
        if subtitle_chunk['text'] != '':
            text_lines = get_text_lines_per_second('', subtitle_chunk['text'], max_text_width, fps, param)
            add_start_time_and_duration(text_lines, subtitle_chunk['start_time'])
        else:
            text_lines = [create_text_obj('', param['FONT_SCALE'], 0, 0)]
            text_lines[0]['frames'] = subtitle_chunk['frames']
            add_start_time_and_duration(text_lines, subtitle_chunk['start_time'])
        subtitles.extend(text_lines)
    return subtitles

def add_start_time_and_duration(text_lines, start_time):
    sum = 0
    for text_line in text_lines:
        sum += text_line['frames']
    current_start_time = start_time
    for text_line in text_lines:
        text_line['start_time'] = current_start_time
        text_line['duration'] = text_line['frames'] / sum
        current_start_time += text_line['duration']

def get_text_lines_per_second(text_old, text, max_text_width, fps, param):
    text_lines = []
    text_old_words = text_old.split(' ')
    text_words = text.split(' ')
    text_sizes = get_size_of_each_word_in_text(text_old_words, text_words, param)
    total_width = 0
    current_text = ''
    current_text_font_scale = param['FONT_SCALE']
    total_new_words_width = 0
    for text_size in text_sizes:
        if total_width + text_size['width'] <= max_text_width:
            if current_text == '':
                current_text = text_size['word']
            else:
                current_text = f'{current_text} {text_size["word"]}'
            total_width += text_size['width']
            if text_size['type'] == 'new':
                total_new_words_width += text_size['width']
        else:
            add_text_obj_to_lines(current_text, current_text_font_scale, text_lines, param)
            current_text = text_size['word']
            total_width = text_size['width']
            if text_size['type'] == 'new':
                total_new_words_width = text_size['width']
            else:
                total_new_words_width = 0
            if total_width > max_text_width:
                current_text_font_scale = get_font_scale_which_fits_text(text_size, max_text_width, param)
                total_new_words_width = max_text_width
            else:
                current_text_font_scale = param['FONT_SCALE']
    add_text_obj_to_lines(current_text, current_text_font_scale, text_lines, param)
    add_duration_to_objs_in_lines(text_lines, fps * param['SUBTITLE_LENGTH'])
    return text_lines

def get_size_of_each_word_in_text(text_old_words, text_words, param):
    text_sizes = []
    for word in text_old_words:
        add_word_obj_to_sizes(word, 'old', text_sizes, param)
    for word in text_words:
        add_word_obj_to_sizes(word, 'new', text_sizes, param)
    return text_sizes

def add_word_obj_to_sizes(word, type, text_sizes, param):
    if word != '':
        text = f'{word} '
        text_dimensions = TextClip(text, fontsize=param['FONT_SCALE'], font=param['TEXT_FONT']).size
        text_width = text_dimensions[0]
        word_size_obj = {}
        word_size_obj['word'] = word
        word_size_obj['width'] = text_width
        word_size_obj['type'] = type
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

def add_text_obj_to_lines(text, font_scale, text_lines, param):
    if text != '':
        text_new_size = TextClip(text, fontsize=font_scale, font=param['TEXT_FONT']).size
        width = text_new_size[0]
        height = text_new_size[1]
        text_obj = create_text_obj(text, font_scale, width, height)
        text_lines.append(text_obj)

def create_text_obj(text, font_scale, width, height):
    text_obj = {}
    text_obj['text'] = text
    text_obj['font_scale'] = font_scale
    text_obj['width'] = width
    text_obj['height'] = height
    return text_obj

def modify_text_obj(text_obj, text, font_scale, width, height):
    text_obj['text'] = text
    text_obj['font_scale'] = font_scale
    text_obj['width'] = width
    text_obj['height'] = height

def get_video_dimensions(video_clip):
    size = video_clip.size
    return size[0], size[1]

