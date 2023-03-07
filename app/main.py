from VideoEditor import MediaAdder, VideoResizer, AudioAdder, VideoClipper
from content_generator import ImageScraper, ImageToVideoCreator
from decoder import SentenceSubjectAnalyzer
from Transcriber import Transcriber, AudioExtractor
from garbage_collection import FileDeleter
from music_adder import MusicAdder
import os

ANGRY_MUSIC_FILE_PATH = '../media_storage/songs/angry/'
CUTE_MUSIC_FILE_PATH = '../media_storage/songs/cute/'
FUNNY_MUSIC_FILE_PATH = '../media_storage/songs/funny/'
MOTIVATIONAL_MUSIC_FILE_PATH = '../media_storage/songs/motivational/'
INTRIGUING_MUSIC_FILE_PATH = '../media_storage/songs/fascinating/'
CONSPIRACY_MUSIC_FILE_PATH = '../media_storage/songs/conspiracy/'

MUSIC_CATEGORY_PATH_DICT = {
    'funny': FUNNY_MUSIC_FILE_PATH,
    'cute': CUTE_MUSIC_FILE_PATH,
    'motivational': MOTIVATIONAL_MUSIC_FILE_PATH,
    'fascinating': INTRIGUING_MUSIC_FILE_PATH,
    'angry': ANGRY_MUSIC_FILE_PATH,
    'conspiracy': CONSPIRACY_MUSIC_FILE_PATH
}

RAW_VIDEO_FILE_PATH = "./media_storage/raw_videos/"
INPUT_FILE_PATH = "./media_storage/InputVideos/"
AUDIO_EXTRACTIONS_PATH = "./media_storage/audio_extractions/"
IMAGE_FILE_PATH = "./media_storage/images/"
IMAGE_2_VIDEOS_FILE_PATH = "./media_storage/videos_made_from_images/"
OUTPUT_FILE_PATH = "./media_storage/OutputVideos/"
ORIGINAL_INPUT_FILE_PATH = "./media_storage/InputVideos/"
CHROME_DRIVER_PATH = "./content_generator/chromedriver.exe"
RESIZED_FILE_PATH = "./media_storage/resized_original_videos/"
VIDEOS_WITH_OVERLAYED_MEDIA_PATH = "./media_storage/media_added_videos/"

def main():
    file_deleter = FileDeleter()
    # print(os.getcwd())
    
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    raw_videos = []
    with open('./media_storage/input_info.csv', 'r') as csv_file:
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
  
    print(raw_videos)
    
    # loop through the files
    for raw_video in raw_videos:
        
        video_clipper = VideoClipper(input_video_file_path=RAW_VIDEO_FILE_PATH,
                                     output_file_path=INPUT_FILE_PATH)
        
        clipped_video = video_clipper.clip_video(raw_video['raw_video_name'],
                                                 raw_video['start_time'],
                                                 raw_video['end_time'])
        
        # resize the video
        video_resizer = VideoResizer(INPUT_FILE_PATH,
                                    RESIZED_FILE_PATH)
        
        resized_video_name = video_resizer.resize_video(clipped_video,
                                                    "resized_" + clipped_video,
                                                    video_resizer.YOUTUBE_SHORT_WIDTH, 
                                                    video_resizer.YOUTUBE_SHORT_HEIGHT)
        
        audio_extractor = AudioExtractor(INPUT_FILE_PATH,
                                        AUDIO_EXTRACTIONS_PATH)
        
        audio_extraction_file_name = audio_extractor.extract_mp3_from_mp4(clipped_video)
                
        # Transcribe the audio file
        # chunk into time segments - for now 8 seconds
        transcriber = Transcriber(AUDIO_EXTRACTIONS_PATH)
        chunk_array = transcriber.run_transcription(audio_extraction_file_name, 5)
        
        print(chunk_array)
        
        # initialize the sentence subject analyzer and image scraper
        analyzer = SentenceSubjectAnalyzer()
        _image_scraper = ImageScraper(CHROME_DRIVER_PATH,
                                    IMAGE_FILE_PATH)
        print("Initialized the sentence subject analyzer and image scraper")
        # for each segment:
        # parse the sentence subject
        # search for and download an image and save the imageID
        # to the _time_stamped_images array
        time_stamped_images = []
        for chunk in chunk_array:
            _sentence_subject = analyzer.parse_sentence_subject(chunk['text'])
            
            _image_id = _image_scraper.search_and_download(_sentence_subject, 1)
            
            if _image_id == None:
                print("No Image found. Skipping.")
                continue
            
            time_stamped_images.append({'start_time': chunk['start_time'],
                                        'end_time': chunk['end_time'], 
                                        'image': _image_id + '.jpg'})
        
        # print the _time_stamped_images array
        print(time_stamped_images)
        
        image_to_video_creator = ImageToVideoCreator(IMAGE_FILE_PATH,
                                                    IMAGE_2_VIDEOS_FILE_PATH)
        
        video_data = image_to_video_creator.process_images(time_stamped_images)
        
        if video_data == None:
            raise Exception("Error: Images were not found. Stopping program.")
        
        media_adder = MediaAdder(RESIZED_FILE_PATH,
                                VIDEOS_WITH_OVERLAYED_MEDIA_PATH,
                                IMAGE_2_VIDEOS_FILE_PATH,
                                OUTPUT_FILE_PATH)
        
        final_video = media_adder.add_videos_to_original_clip(original_clip=resized_video_name,
                                        videos=video_data,
                                        original_clip_width=media_adder.YOUTUBE_SHORT_WIDTH,
                                        original_clip_height=media_adder.YOUTUBE_SHORT_HALF_HEIGHT * 2,
                                        overlay_zone_width=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_WIDTH,
                                        overlay_zone_height=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_HEIGHT,
                                        overlay_zone_x=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_X,
                                        overlay_zone_y=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_Y)

        print("Finished adding videos to original clip")
        
        myMusicAdder = MusicAdder(music_file_paths=MUSIC_CATEGORY_PATH_DICT,
                          video_files_path='../media_storage/OutputVideos/',
                          output_path='../media_storage/OutputVideos/')

        myMusicAdder.add_music_to_video(music_category=raw_video['music_category'],
                                        video_name=final_video,
                                        video_length=ceil(video_data['start_time']['end_time']))

        
        # audioAdder = AudioAdder(OUTPUT_FILE_PATH, AUDIO_EXTRACTIONS_PATH)

        # audioAdder.combine_video_audio(final_video, audio_extraction_file_name)
        
        # file_deleter.delete_files_from_folder(IMAGE_2_VIDEOS_FILE_PATH)
        # file_deleter.delete_files_from_folder(IMAGE_FILE_PATH)
        
    

 
main()