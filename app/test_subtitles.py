from VideoEditor import MediaAdder, VideoResizer, VideoClipper

from text_analyzer import SentenceSubjectAnalyzer
from Transcriber import WhisperTranscriber, AudioExtractor
from music_adder import MusicAdder
from subtitle_adder import SubtitleAdder
import configuration.presets as presets
import os
import math
import logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

root = "../test_material"

RAW_VIDEO_FILE_PATH = f"{root}/raw_videos/"
INPUT_FILE_PATH = f"{root}/InputVideos/"
AUDIO_EXTRACTIONS_PATH = f"{root}/audio_extractions/"
IMAGE_FILE_PATH = f"{root}/images/"
IMAGE_2_VIDEOS_FILE_PATH = f"{root}/videos_made_from_images/"
OUTPUT_FILE_PATH = f"{root}/OutputVideos/"
INPUT_PATH = f"{root}/InputVideos/"
RESIZED_FILE_PATH = f"{root}/resized_original_videos/"

def main():
    
    
    print(os.getcwd())
    
    transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH, transcripts_folder=AUDIO_EXTRACTIONS_PATH)
    subtitle_adder = SubtitleAdder(INPUT_PATH, OUTPUT_FILE_PATH)

    # Transcribe the audio file
    transcription = transcriber.transcribe("goggins.mp3")
    theme = presets.themes['curious_primates']
    
    video_with_subtitles_name = subtitle_adder.add_subtitles_to_video(video_file_name="goggins.mp4",
                                            transcription=transcription['word_segments'],
                                            output_file_name='sub_' + "goggins.mp4",
                                            font_size=theme['FONT_SIZE'],
                                            font_name=theme['FONT'],
                                            outline_color=theme['FONT_OUTLINE_COLOR'],
                                            outline_width=theme['FONT_OUTLINE_WIDTH'],
                                            font_color=theme['FONT_COLOR'],
                                            all_caps=theme['ALL_CAPS'],
                                            punctuation=theme['PUNCTUATION'],
                                            y_percent=theme["Y_PERCENT_HEIGHT_OF_SUBTITLE"],
                                            number_of_characters_per_line=theme["NUMBER_OF_CHARACTERS_PER_LINE"],
                                            interval=theme["SUBTITLE_DURATION"])

        
        

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


 
main()
# from moviepy.editor import TextClip
# print ( TextClip.list("color") )
