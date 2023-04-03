from VideoEditor import MediaAdder, VideoResizer, VideoClipper
from content_generator import ImageScraper, ImageToVideoCreator, DALL_E
from decoder import SentenceSubjectAnalyzer
from Transcriber import WhisperTranscriber, AudioExtractor
from garbage_collection import FileDeleter
from music_adder import MusicAdder
from subtitle_adder import SubtitleAdderMv
import os
import math
import logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

root = "./"

RAW_VIDEO_FILE_PATH = f"{root}media_storage/raw_videos/"
INPUT_FILE_PATH = f"{root}media_storage/InputVideos/"
AUDIO_EXTRACTIONS_PATH = f"{root}media_storage/audio_extractions/"
IMAGE_FILE_PATH = f"{root}media_storage/images/"
IMAGE_2_VIDEOS_FILE_PATH = f"{root}media_storage/videos_made_from_images/"
OUTPUT_FILE_PATH = f"{root}media_storage/OutputVideos/"
ORIGINAL_INPUT_FILE_PATH = f"{root}media_storage/InputVideos/"
CHROME_DRIVER_PATH = f"{root}content_generator/chromedriver.exe"
RESIZED_FILE_PATH = f"{root}media_storage/resized_original_videos/"
VIDEOS_WITH_OVERLAYED_MEDIA_PATH = f"{root}media_storage/media_added_videos/"
QUERY_FILE_PATH = f'{root}media_storage/queries/'
INPUT_INFO_FILE_LOCATION = f'{root}media_storage/input_info.csv'

def main():
    
    
    print(os.getcwd())
    
    video_clipper = VideoClipper(input_video_file_path=RAW_VIDEO_FILE_PATH,
                                     output_file_path=INPUT_FILE_PATH)
    video_resizer = VideoResizer(INPUT_FILE_PATH,
                            RESIZED_FILE_PATH)
    audio_extractor = AudioExtractor(INPUT_FILE_PATH,
                                    AUDIO_EXTRACTIONS_PATH)
    transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH, CLEAN_SUBTITLES=True)
    subtitle_adder = SubtitleAdderMv(RESIZED_FILE_PATH,
                                        OUTPUT_FILE_PATH)
    
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    raw_videos = get_raw_videos()
  
    print(raw_videos)

    # loop through the files
    for raw_video in raw_videos:
        
        
        clipped_video = video_clipper.clip_video(raw_video['raw_video_name'],
                                                 raw_video['start_time'],
                                                 raw_video['end_time'])
        
        # resize the video

        resized_video_name = video_resizer.resize_video(clipped_video['file_name'],
                                                        clipped_video['file_name'],
                                                        video_resizer.YOUTUBE_SHORT_WIDTH, 
                                                        video_resizer.YOUTUBE_SHORT_HEIGHT)

        audio_extraction_file_name = audio_extractor.extract_mp3_from_mp4(clipped_video['file_name'])
        
        # Transcribe the audio file
        transcription = transcriber.transcribe(audio_extraction_file_name)
        
        
        
        
        

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_raw_videos():
    raw_videos = []
    with open(INPUT_INFO_FILE_LOCATION, 'r') as csv_file:
        for line in csv_file:
            # skip the first line
            if line == "raw_video_name,start_time,end_time,music_category\n":
                continue
            line = line.strip()
            line = line.split(',')
            raw_videos.append({'raw_video_name': str(line[0]),
                                'start_time': str(line[1]),
                                'end_time': str(line[2]),
                                'music_category': str(line[3])})
            
    return raw_videos

 
# main()
from moviepy.editor import TextClip
print ( TextClip.list("font") )
# save the contents of the list to a file called "fonts.txt"
with open("fonts.txt", "w") as f:
    for font in TextClip.list("font"):
        f.write(font + "\n")