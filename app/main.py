from VideoEditor import MediaAdder, VideoResizer, AudioAdder
from content_generator import ImageScraper, ImageToVideoCreator
from decoder import SentenceSubjectAnalyzer
from Transcriber import Transcriber, AudioExtractor
from garbage_collection import FileDeleter
import os

INPUT_FILE_PATH = "./InputVideos/"
AUDIO_EXTRACTIONS_PATH = "./audio_extractions/"
IMAGE_FILE_PATH = "./images/"
IMAGE_2_VIDEOS_FILE_PATH = "./videos_made_from_images/"
OUTPUT_FILE_PATH = "./OutputVideos/"
ORIGINAL_INPUT_FILE_PATH = "./InputVideos/"
CHROME_DRIVER_PATH = "./content_generator/chromedriver.exe"
RESIZED_FILE_PATH = "./resized_original_videos/"
VIDEOS_WITH_OVERLAYED_MEDIA_PATH = "./media_added_videos/"

def main():
    file_deleter = FileDeleter()
    # print(os.getcwd())
    
    # get the names of all the files in the input folder
    input_file_names = os.listdir(INPUT_FILE_PATH)
    
    # loop through the files
    for original_video_name in input_file_names:
    
        # resize the video
        video_resizer = VideoResizer(INPUT_FILE_PATH,
                                    RESIZED_FILE_PATH)
        
        resized_video_name = video_resizer.resize_video(original_video_name,
                                                    "resized_" + original_video_name,
                                                    video_resizer.YOUTUBE_SHORT_WIDTH, 
                                                    video_resizer.YOUTUBE_SHORT_HEIGHT)
        
        audio_extractor = AudioExtractor(INPUT_FILE_PATH,
                                        AUDIO_EXTRACTIONS_PATH)
        
        audio_extraction_file_name = audio_extractor.extract_mp3_from_mp4(original_video_name)
                
        # Transcribe the audio file
        # chunk into time segments - for now 8 seconds
        transcriber = Transcriber(AUDIO_EXTRACTIONS_PATH)
        chunk_array = transcriber.run_transcription(audio_extraction_file_name, 8)

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
        
        audioAdder = AudioAdder(OUTPUT_FILE_PATH, AUDIO_EXTRACTIONS_PATH)

        audioAdder.combine_video_audio(final_video, audio_extraction_file_name)
        
     
 
main()