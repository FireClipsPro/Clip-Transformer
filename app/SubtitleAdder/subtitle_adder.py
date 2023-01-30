import math
import cv2
import ffmpeg
import os
import sys
from pathlib import Path

current_path = Path(os.path.abspath(__file__)).resolve()
transcriber_path = os.path.join(current_path.parent.parent, 'Transcriber')
sys.path.append(transcriber_path)

audio_adder_path = os.path.join(current_path.parent.parent, 'VideoEditor')
sys.path.append(audio_adder_path)

from text_timestamper import TextTimeStamper
from transcriber import Transcriber
import transcriber_utils
from audio_adder import AudioAdder

class SubtitleAdder:

    TEXT_FONT = cv2.FONT_HERSHEY_TRIPLEX
    FONT_SCALE = 1
    TEXT_THICKNESS = 2
    TEXT_COLOUR = (255, 255, 255)
    SUBTITLE_LENGTH = 1
    SUBTITLE_HORIZONTAL_WIDTH = 0.2

    def __init__(self):
        pass

    def add_subtitles(self, path, transcript):
        video_cap = cv2.VideoCapture(path)
        fps, fc = self.get_frames_per_second_and_frame_count(video_cap, path)
        video_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        path_resolve = Path(path).resolve()
        file_name = f'{path_resolve.stem}-out.mp4'
        output_path = os.path.join(path_resolve.parent, file_name)
        out = cv2.VideoWriter(output_path, fourcc, fps, (video_width, video_height))
        increment = int(video_height / 40)
        max_text_width = int(self.SUBTITLE_HORIZONTAL_WIDTH * video_width)
        text_top = ''
        text_bottom = ''
        x_start = (1 - self.SUBTITLE_HORIZONTAL_WIDTH) / 2
        text_x = int(x_start * video_width)
        text_top_y = int(video_height / 2) - increment
        curr_frames = 0
        duration_of_silence = 0
        frames_per_subtitle = self.get_frames_per_subtitle_add(transcript, fps)
        subtitles = self.configure_subtitles_to_frames(frames_per_subtitle, max_text_width, fps)
        subtitles.reverse()
        while video_cap.isOpened():
            if curr_frames == 0:
                if len(subtitles) == 0:
                    curr_frames = -1
                    text_top = ''
                    text_bottom = ''
                else:
                    text_per_frames_obj = subtitles.pop()
                    curr_frames = text_per_frames_obj['frames']
                    if text_per_frames_obj['text'] != '':
                        duration_of_silence = 0
                        if text_bottom == '':
                            new_text = f'{text_per_frames_obj["text"]}'
                        else:
                            new_text = f'{text_bottom} {text_per_frames_obj["text"]}'
                        text_new_size = cv2.getTextSize(new_text, self.TEXT_FONT, self.FONT_SCALE, self.TEXT_THICKNESS)
                        text_new_width = text_new_size[0][0]
                        if text_new_width > max_text_width:
                            text_top = text_bottom
                            text_bottom = text_per_frames_obj["text"]
                        else:
                            text_bottom = new_text
                    else:
                        duration_of_silence += 1
                        if 3 <= duration_of_silence < 5:
                            text_top = ''
                        elif duration_of_silence >= 5:
                            text_bottom = ''

            retVal, frame = video_cap.read()
            if not retVal:
                break
            text_bottom_size = cv2.getTextSize(text_bottom, self.TEXT_FONT, self.FONT_SCALE, self.TEXT_THICKNESS)
            text_bottom_height = text_bottom_size[0][1]
            if text_top != '':
                text_bottom_y = int((video_height / 2) + text_bottom_height + increment)
            else:
                text_bottom_y = int((video_height / 2))
            new_frame = cv2.putText(frame, text_top, (text_x, text_top_y), self.TEXT_FONT, self.FONT_SCALE,
                                    self.TEXT_COLOUR, self.TEXT_THICKNESS)
            new_frame = cv2.putText(new_frame, text_bottom, (text_x, text_bottom_y), self.TEXT_FONT,
                                    text_per_frames_obj['font_scale'], self.TEXT_COLOUR, self.TEXT_THICKNESS)
            out.write(new_frame)
            cv2.imshow("Subtitled Video", new_frame)
            curr_frames -= 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_cap.release()
        out.release()
        cv2.destroyAllWindows()
        return output_path

    def configure_subtitles_to_frames(self, frames_per_subtitle, max_text_width, fps):
        subtitles = []
        for subtitle_chunk in frames_per_subtitle:
            text_dimensions = cv2.getTextSize(subtitle_chunk['text'],
                                              self.TEXT_FONT, self.FONT_SCALE, self.TEXT_THICKNESS)
            text_width = text_dimensions[0][0]
            if text_width > max_text_width:
                text_lines = self.get_text_lines_per_second('', subtitle_chunk['text'], max_text_width, fps)
                subtitles.extend(text_lines)
            else:
                subtitle_chunk['font_scale'] = self.FONT_SCALE
                subtitles.append(subtitle_chunk)
        return subtitles


    def add_text_lines_to_frames_per_subtitle(self, text_lines, frames_per_subtitle):
        text_lines.reverse()
        for line in text_lines:
            frames_per_subtitle.append(line)


    def get_frames_per_second_and_frame_count(self, video_cap, path):
        try:
            fps = int(video_cap.get(cv2.CAP_PROP_FPS))
            fc = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if fps == 0 or fc == 0:
                fps, fc = self.get_frames_per_second_and_frame_count_ffmpeg(path)
        except:
            fps, fc = self.get_frames_per_second_and_frame_count_ffmpeg(path)
        finally:
            fps = math.ceil(fps)
            return fps, fc


    def get_frames_per_second_and_frame_count_ffmpeg(self, path):
        probe = ffmpeg.probe(path)
        video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        fps = float(video_stream['r_frame_rate'])
        fc = int(probe['streams'][0]['nb_frames'])
        return fps, fc

    def get_frames_per_subtitle_add(self, transcript, fps):
        result = []
        text_time_stamper = TextTimeStamper()
        stamped_text = text_time_stamper.timestamp_chunk_of_text(transcript, self.SUBTITLE_LENGTH)
        size = len(stamped_text)
        for i, text_object in enumerate(stamped_text):
            if i == 0 and text_object['start_time'] != 0:
                text_per_frames_obj = {}
                text_per_frames_obj['text'] = ''
                text_per_frames_obj['frames'] = text_object['start_time'] * fps
                result.append(text_per_frames_obj)
                continue
            text_per_frames_obj = {}
            text_per_frames_obj['text'] = text_object['text']
            text_per_frames_obj['frames'] = self.SUBTITLE_LENGTH * fps
            result.append(text_per_frames_obj)
            if i + 1 < size:
                text_duration_btw_curr_next = abs(stamped_text[i + 1]['start_time'] - text_object['end_time'])
                if text_duration_btw_curr_next > 1:
                    text_per_frames_obj = {}
                    text_per_frames_obj['text'] = ''
                    text_per_frames_obj['frames'] = (text_duration_btw_curr_next - 1) * fps
                    result.append(text_per_frames_obj)

        return result


    def get_text_lines_per_second(self, text_old, text, max_text_width, fps):
        text_lines = []
        text_old_words = text_old.split(' ')
        text_words = text.split(' ')
        text_sizes = self.get_size_of_each_word_in_text(text_old_words, text_words)
        total_width = 0
        current_text = ''
        current_text_font_scale = self.FONT_SCALE
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
                # need to add the text duration (in frames) later
                self.add_text_obj_to_lines(current_text, current_text_font_scale, total_new_words_width, text_lines)
                current_text = text_size['word']
                total_width = text_size['width']
                if text_size['type'] == 'new':
                    total_new_words_width = text_size['width']
                else:
                    total_new_words_width = 0
                # handle edge case where current_text (single word) has higher width than max_text_width.
                # solve by reducing font scale by half every time until it fits (< or = to max_text_width).
                if total_width > max_text_width:
                    current_text_font_scale = self.get_font_scale_which_fits_text(text_size, max_text_width)
                    total_new_words_width = max_text_width
                else:
                    current_text_font_scale = self.FONT_SCALE
        self.add_text_obj_to_lines(current_text, current_text_font_scale, total_width, text_lines)
        self.add_duration_to_objs_in_lines(text_lines, fps * self.SUBTITLE_LENGTH)
        return text_lines


    def add_duration_to_objs_in_lines(self, text_lines, total_frames):
        sum = 0
        total_frames_used = 0
        for line in text_lines:
            sum += line['width']
        last_line = text_lines.pop()
        for line in text_lines:
            line['frames'] = int(math.floor(total_frames * (line['width'] / sum)))
            total_frames_used += line['frames']
        # adjust last line in text_lines
        last_line['frames'] = total_frames - total_frames_used
        text_lines.append(last_line)


    def add_text_obj_to_lines(self, text, font_scale, width, text_lines):
        if text != '':
            text_per_frames_obj = {}
            text_per_frames_obj['text'] = text
            text_per_frames_obj['font_scale'] = font_scale
            text_per_frames_obj['width'] = width
            text_lines.append(text_per_frames_obj)

    def get_size_of_each_word_in_text(self, text_old_words, text_words):
        text_sizes = []
        for word in text_old_words:
            self.add_word_obj_to_sizes(word, 'old', text_sizes)
        for word in text_words:
            self.add_word_obj_to_sizes(word, 'new', text_sizes)
        return text_sizes

    def add_word_obj_to_sizes(self, word, type, text_sizes):
        if word != '':
            text = f'{word} '
            text_dimensions = cv2.getTextSize(text, self.TEXT_FONT, self.FONT_SCALE, self.TEXT_THICKNESS)
            text_width = text_dimensions[0][0]
            word_size_obj = {}
            word_size_obj['word'] = word
            word_size_obj['width'] = text_width
            word_size_obj['type'] = type
            text_sizes.append(word_size_obj)



#   Recreate using binary search to make time complexity O(logn)
    def get_font_scale_which_fits_text(self, text_size, max_text_width):
        font_scale_decrease_per_iter = 0.01
        i = 1
        while True:
            new_font_scale = self.FONT_SCALE * (1 - (i * font_scale_decrease_per_iter))
            if new_font_scale <= 0:
                break
            new_text_dimensions = cv2.getTextSize(text_size['word'], self.TEXT_FONT, new_font_scale, self.TEXT_THICKNESS)
            new_text_width = new_text_dimensions[0][0]
            if new_text_width <= max_text_width:
                return new_font_scale
            i += 1
        raise Exception('Decrease font_scale_decrease_per_iter parameter as text isn\'t fitting')





transcriber = Transcriber()
chunk_length = 6

joe_elon_tesla_mp3_clip = '../videos/JoeElonTesla.mp3'
joe_elon_tesla_mp3_clip_json = '../Vault/JoeElonTesla_short.txt'
joe_elon_tesla_mp3_absolute_path = transcriber_utils.get_absolute_path(__file__, joe_elon_tesla_mp3_clip)
joe_elon_tesla_mp3_json_absolute_path = transcriber_utils.get_absolute_path(__file__, joe_elon_tesla_mp3_clip_json)
# transcription, stamped_texts = transcriber.transcribe_audio_file(joe_elon_tesla_mp3_absolute_path, chunk_length)
transcription = transcriber_utils.load_transcription(joe_elon_tesla_mp3_json_absolute_path)

joe_long_mp3_clip = '../videos/TestAudioExtraction.mp3'
joe_long_mp3_clip_json = '../Vault/JoeLong_long.txt'
joe_long_mp3_json_absolute_path = transcriber_utils.get_absolute_path(__file__, joe_long_mp3_clip_json)
# transcription, stamped_texts = transcriber.transcribe_audio_file(joe_elon_tesla_mp3_absolute_path, chunk_length)
# transcription = transcriber_utils.load_transcription(joe_long_mp3_json_absolute_path)


joe_long_mp4_clip = '../videos/JoeElonTesla.mp4'
joe_long_mp4_absolute_path = transcriber_utils.get_absolute_path(__file__, joe_long_mp4_clip)
sub_adder = SubtitleAdder()
output_file_path = sub_adder.add_subtitles(joe_long_mp4_absolute_path, transcription)
audio_adder = AudioAdder()
output_final_file_path = audio_adder.add_audio_to_video(joe_elon_tesla_mp3_absolute_path, output_file_path)
print(output_final_file_path)
