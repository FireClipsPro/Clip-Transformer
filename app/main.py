from VideoEditor import MediaAdder, VideoResizer, VideoClipper, HeadTrackingCropper, ImageSpacer, PauseRemover
from content_generation import ImageScraper, ImageToVideoCreator, DALL_E, ImageGetter, GoogleImagesAPI, ImageClassifier, ImageEvaluator, FullScreenImageSelector
from text_analyzer import SentenceSubjectAnalyzer, TranscriptAnalyzer, OpenaiApi
from Transcriber import WhisperTranscriber, AudioExtractor
from garbage_collection import FileDeleter
from music_adder import MusicAdder
from subtitle_adder import SubtitleAdder
import os
import math
import logging
import time
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

VERTICAL_VIDEO_HEIGHT = 1920
VERTICAL_VIDEO_WIDTH = 1080
HEAD_TRACKING_ENABLED = True
SECONDS_PER_PHOTO = 6
PERECENT_OF_IMAGES_TO_BE_FULLSCREEN = 0.3
MAXIMUM_PAUSE_LENGTH = 0.5
TIME_BETWEEN_IMAGES = 1.5

root = "../media_storage/"

ANGRY_MUSIC_FOLDER = f'{root}songs/angry/'
CUTE_MUSIC_FOLDER = f'{root}songs/cute/'
FUNNY_MUSIC_FOLDER = f'{root}songs/funny/'
MOTIVATIONAL_MUSIC_FOLDER = f'{root}songs/motivational/'
INTRIGUING_MUSIC_FOLDER = f'{root}songs/fascinating/'
CONSPIRACY_MUSIC_FOLDER = f'{root}songs/conspiracy/'

MUSIC_CATEGORY_PATH_DICT = {
    'funny': FUNNY_MUSIC_FOLDER,
    'cute': CUTE_MUSIC_FOLDER,
    'motivational': MOTIVATIONAL_MUSIC_FOLDER,
    'fascinating': INTRIGUING_MUSIC_FOLDER,
    'angry': ANGRY_MUSIC_FOLDER,
    'conspiracy': CONSPIRACY_MUSIC_FOLDER
}

RAW_VIDEO_FOLDER = f"{root}raw_videos/"
INPUT_FOLDER = f"{root}InputVideos/"
AUDIO_EXTRACTIONS_FOLDER = f"{root}audio_extractions/"
IMAGE_FOLDER = f"{root}images/"
IMAGE_2_VIDEOS_FOLDER = f"{root}videos_made_from_images/"
OUTPUT_FOLDER = f"{root}OutputVideos/"
ORIGINAL_INPUT_FOLDER = f"{root}InputVideos/"
CHROME_DRIVER_PATH = f"{root}content_generator/chromedriver.exe"
RESIZED_FOLDER = f"{root}resized_original_videos/"
VIDEOS_WITH_OVERLAYED_MEDIA_PATH = f"{root}media_added_videos/"
QUERY_FOLDER = f'{root}queries/'
INPUT_INFO_FOLDER = f'{root}input_info.csv'
VIDEO_INFO_FOLDER = f"{root}video_info/"
GENERATED_PROMPTS_FOLDER = f"{root}generated_prompts/"

def main():
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    raw_videos = get_raw_videos()
    print(raw_videos)
    
    video_clipper = VideoClipper(input_video_file_path=RAW_VIDEO_FOLDER,
                                 output_file_path=INPUT_FOLDER)
    
    audio_extractor = AudioExtractor(INPUT_FOLDER,
                                     AUDIO_EXTRACTIONS_FOLDER)

    transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_FOLDER)
    
    pause_remover = PauseRemover(INPUT_FOLDER, RESIZED_FOLDER)
    
    head_tracker = HeadTrackingCropper(RESIZED_FOLDER,
                                       RESIZED_FOLDER)
    video_resizer = VideoResizer(INPUT_FOLDER,
                                 RESIZED_FOLDER)
    
    openai_api = OpenaiApi()

    transcription_analyzer = TranscriptAnalyzer(VIDEO_INFO_FOLDER,
                                                MUSIC_CATEGORY_PATH_DICT,
                                                openai_api)

    sentence_analyzer = SentenceSubjectAnalyzer(QUERY_FOLDER,
                                                openai_api)
    
    image_spacer = ImageSpacer()
    
    image_classifier = ImageClassifier(IMAGE_FOLDER)
    
    image_evaluator = ImageEvaluator(IMAGE_FOLDER)

    image_scraper = GoogleImagesAPI(IMAGE_FOLDER,
                                    image_classifier,
                                    image_evaluator)
    
    image_getter = ImageGetter(IMAGE_FOLDER,
                               image_scraper,
                               image_evaluator)

    dall_e = DALL_E(IMAGE_FOLDER,
                    GENERATED_PROMPTS_FOLDER)
    
    fullscreen_image_selector = FullScreenImageSelector(IMAGE_FOLDER,
                                                        image_evaluator=image_evaluator)

    image_to_video_creator = ImageToVideoCreator(IMAGE_FOLDER,
                                                 IMAGE_2_VIDEOS_FOLDER,
                                                 image_evaluator=image_evaluator)

    media_adder = MediaAdder(RESIZED_FOLDER,
                    VIDEOS_WITH_OVERLAYED_MEDIA_PATH,
                    IMAGE_2_VIDEOS_FOLDER,
                    OUTPUT_FOLDER)

    subtitle_adder = SubtitleAdder(OUTPUT_FOLDER,
                                    OUTPUT_FOLDER)

    music_adder = MusicAdder(music_file_paths=MUSIC_CATEGORY_PATH_DICT,
                        video_files_path=OUTPUT_FOLDER,
                        output_path=OUTPUT_FOLDER,
                        music_categories=MUSIC_CATEGORY_PATH_DICT)

    # loop through the files
    for raw_video in raw_videos:
        
        clipped_video = video_clipper.clip_video(raw_video['raw_video_name'],
                                                 raw_video['start_time'],
                                                 raw_video['end_time'],
                                                 raw_video['tag'])
        
        audio_extraction_file_name = audio_extractor.extract_mp3_from_mp4(clipped_video['file_name'])
        
        transcription = transcriber.transcribe(audio_extraction_file_name)
        
        clipped_video, transcription['word_segments'] = pause_remover.remove_pauses(clipped_video,
                                                                                    transcription['word_segments'],
                                                                                    MAXIMUM_PAUSE_LENGTH)
        
        if HEAD_TRACKING_ENABLED:
            clipped_video = head_tracker.crop_video_to_face_center(clipped_video,
                                                                    VERTICAL_VIDEO_WIDTH,
                                                                    VERTICAL_VIDEO_HEIGHT)
        else:
            clipped_video = video_resizer.resize_video(clipped_video['file_name'],
                                                        clipped_video['file_name'],
                                                        video_resizer.YOUTUBE_VIDEO_WIDTH * 0.8, 
                                                        video_resizer.YOUTUBE_VIDEO_HEIGHT,
                                                        clipped_video) 

        
        clipped_video = transcription_analyzer.get_info(clipped_video, transcription)
        
        query_list = sentence_analyzer.process_transcription(transcription['word_segments'],
                                                    transcription['word_segments'][-1]['end'],
                                                    SECONDS_PER_PHOTO,
                                                    clipped_video['transcription_info']['description'],
                                                    clipped_video['file_name'])
        
        query_list = image_spacer.add_spacing_to_images(query_list,
                                                        time_between_images=TIME_BETWEEN_IMAGES)
        
        time_stamped_images = image_getter.get_images(query_list)
                
        # where images could not be found, DALL-E will be used to generate images
        time_stamped_images = dall_e.generate_images(time_stamped_images)
        
        # print the _time_stamped_images array
        print(time_stamped_images)
        
        # add fullscreenimageselector here
        time_stamped_images = fullscreen_image_selector.choose_fullscreen_images(time_stamped_images,
                                                                                 VERTICAL_VIDEO_WIDTH,
                                                                                 VERTICAL_VIDEO_HEIGHT,
                                                                                 VERTICAL_VIDEO_WIDTH,
                                                                                 int(VERTICAL_VIDEO_HEIGHT / 2),
                                                                                 percent_of_images_to_be_fullscreen=PERECENT_OF_IMAGES_TO_BE_FULLSCREEN)
        
        video_data = image_to_video_creator.convert_to_videos(time_stamped_images)
        
        video_with_media = media_adder.add_videos_to_original_clip(original_clip=clipped_video,
                                        videos=video_data,
                                        original_clip_width=media_adder.YOUTUBE_SHORT_WIDTH,
                                        original_clip_height=media_adder.YOUTUBE_SHORT_HALF_HEIGHT * 2)
    
        video_with_subtitles_name = subtitle_adder.add_subtitles_to_video(video_with_media['file_name'],
                                                                 transcription['word_segments'],
                                                                 'sub_' + video_with_media['file_name'],
                                                                 80,
                                                                 'Tahoma Bold.ttf',
                                                                 50,
                                                                 50,
                                                                 1)

        video_with_music_name = music_adder.add_music_to_video(music_category=clipped_video['transcription_info']['category'],
                                        video_name=video_with_subtitles_name,
                                        output_video_name=clipped_video['transcription_info']['title'],
                                        video_length=math.ceil(float(
                                                                    clipped_video['end_time_sec']) 
                                                                    - float(clipped_video['start_time_sec'])))
        video_clipper.output_file_path = OUTPUT_FOLDER
        video_clipper.input_video_folder_path = OUTPUT_FOLDER
        video_clipper.clip_video(video_with_music_name,
                                 0,
                                 clipped_video['end_time_sec'])
        video_clipper.input_video_folder_path = RAW_VIDEO_FOLDER
        video_clipper.output_file_path = INPUT_FOLDER

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_raw_videos():
    raw_videos = []
    with open(INPUT_INFO_FOLDER, 'r') as csv_file:
        for line in csv_file:
            # skip the first line
            if line == "raw_video_name,start_time,end_time,tag\n":
                continue
            line = line.strip()
            line = line.split(',')
            if str(line[3]) == '-1':
                tag = ""
            else:
                tag = str(line[3]) + "_"
            
            raw_videos.append({'raw_video_name': str(line[0]),
                                'start_time': str(line[1]),
                                'end_time': str(line[2]),
                                'tag': tag})
            
    return raw_videos

 
main()