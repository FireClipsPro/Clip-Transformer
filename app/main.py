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

ANGRY_MUSIC_FILE_PATH = f'{root}media_storage/songs/angry/'
CUTE_MUSIC_FILE_PATH = f'{root}media_storage/songs/cute/'
FUNNY_MUSIC_FILE_PATH = f'{root}media_storage/songs/funny/'
MOTIVATIONAL_MUSIC_FILE_PATH = f'{root}media_storage/songs/motivational/'
INTRIGUING_MUSIC_FILE_PATH = f'{root}media_storage/songs/fascinating/'
CONSPIRACY_MUSIC_FILE_PATH = f'{root}media_storage/songs/conspiracy/'

MUSIC_CATEGORY_PATH_DICT = {
    'funny': FUNNY_MUSIC_FILE_PATH,
    'cute': CUTE_MUSIC_FILE_PATH,
    'motivational': MOTIVATIONAL_MUSIC_FILE_PATH,
    'fascinating': INTRIGUING_MUSIC_FILE_PATH,
    'angry': ANGRY_MUSIC_FILE_PATH,
    'conspiracy': CONSPIRACY_MUSIC_FILE_PATH
}

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
    video_clipper = VideoClipper(input_video_file_path=RAW_VIDEO_FILE_PATH,
                                    output_file_path=INPUT_FILE_PATH)
    video_resizer = VideoResizer(INPUT_FILE_PATH,
                                RESIZED_FILE_PATH)
    audio_extractor = AudioExtractor(INPUT_FILE_PATH,
                                    AUDIO_EXTRACTIONS_PATH)
    transcriber = WhisperTranscriber(AUDIO_EXTRACTIONS_PATH)
    analyzer = SentenceSubjectAnalyzer(QUERY_FILE_PATH)
    image_scraper = ImageScraper(CHROME_DRIVER_PATH,
                                IMAGE_FILE_PATH)
    dall_e = DALL_E(IMAGE_FILE_PATH)
    image_to_video_creator = ImageToVideoCreator(IMAGE_FILE_PATH,
                                                IMAGE_2_VIDEOS_FILE_PATH)
    media_adder = MediaAdder(RESIZED_FILE_PATH,
                    VIDEOS_WITH_OVERLAYED_MEDIA_PATH,
                    IMAGE_2_VIDEOS_FILE_PATH,
                    OUTPUT_FILE_PATH)
    subtitle_adder = SubtitleAdderMv(OUTPUT_FILE_PATH,
                                    OUTPUT_FILE_PATH)
    music_adder = MusicAdder(music_file_paths=MUSIC_CATEGORY_PATH_DICT,
                        video_files_path=OUTPUT_FILE_PATH,
                        output_path=OUTPUT_FILE_PATH)

    
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    raw_videos = get_raw_videos()
    print(raw_videos)

    # loop through the files
    for raw_video in raw_videos:
        
        clipped_video = video_clipper.clip_video(raw_video['raw_video_name'],
                                                 raw_video['start_time'],
                                                 raw_video['end_time'])
        
        resized_video_name = video_resizer.resize_video(clipped_video['file_name'],
                                                        clipped_video['file_name'],
                                                        video_resizer.YOUTUBE_SHORT_WIDTH, 
                                                        video_resizer.YOUTUBE_SHORT_HEIGHT)

        audio_extraction_file_name = audio_extractor.extract_mp3_from_mp4(clipped_video['file_name'])
        
        # Transcribe the audio file
        transcription = transcriber.transcribe(audio_extraction_file_name)
        
        
        print("Initialized the sentence subject analyzer and image scraper")
        query_list = analyzer.process_transcription(transcription['segments'],
                                                    transcription['segments'][-1]['end'],
                                                    6,
                                                    raw_video['raw_video_name'])
        
        time_stamped_images = []
        for query in query_list:
            image_id = image_scraper.search_and_download(query['query'], 1)
            
            if image_id == None:
                time_stamped_images.append({'start_time': query['start'],
                                            'end_time': query['end'], 
                                            'image': '_Nothing_Found_' + query['query']})
            else:
                time_stamped_images.append({'start_time': query['start'],
                                            'end_time': query['end'], 
                                            'image': image_id.replace(" ", "_") + '.jpg'})
        
        # where images could not be found, DALL-E will be used to generate images
        time_stamped_images = dall_e.generate_images(time_stamped_images)
        
        # print the _time_stamped_images array
        print(time_stamped_images)
        
        video_data = image_to_video_creator.process_images(time_stamped_images)
        if video_data == None:
            raise Exception("Error: Images were not found. Stopping program.")
        
        video_with_media = media_adder.add_videos_to_original_clip(original_clip=video_with_subtitles_name,
                                        videos=video_data,
                                        original_clip_width=media_adder.YOUTUBE_SHORT_WIDTH,
                                        original_clip_height=media_adder.YOUTUBE_SHORT_HALF_HEIGHT * 2,
                                        overlay_zone_width=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_WIDTH,
                                        overlay_zone_height=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_HEIGHT,
                                        overlay_zone_x=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_X,
                                        overlay_zone_y=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_Y)
        
        video_with_subtitles_name = subtitle_adder.subtitle_adder(video_with_media, transcription, 50, 'Tahoma-Bold')

        music_adder.add_music_to_video(music_category=raw_video['music_category'],
                                        video_name=video_with_media,
                                        video_length=math.ceil(float(clipped_video['end_time_sec']) - float(clipped_video['start_time_sec'])))

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

 
main()