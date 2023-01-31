from VideoEditor import MediaAdder, VideoResizer, AudioAdder
from content_generator import ImageScraper, ImageToVideoCreator
from decoder import SentenceSubjectAnalyzer
from Transcriber import Transcriber, AudioExtractor
import os

RESIZED_FILE_PATH = './OutputVideos/'
INPUT_FILE_PATH = './InputVideos/'
AUDIO_EXTRACTIONS_PATH = './audio_extractions/'
IMAGE_FILE_PATH = './images/'
IMAGE_2_VIDEOS_FILE_PATH = './ImageVideos/'
OUTPUT_FILE_PATH = "./OutputVideos/"
ORIGINAL_INPUT_FILE_PATH = "./InputVideos/"
CHROME_DRIVER_PATH = "./content_generator/chromedriver.exe"

def main():
    # print(os.getcwd())
    # return
    # get original video
    original_video = 'JordanClip.mp4'
    # resize the video
    video_resizer = VideoResizer(INPUT_FILE_PATH,
                                 RESIZED_FILE_PATH)
    
    resized_video = video_resizer.resize_video(original_video,
                                                "JordanClipResized.mp4",
                                                video_resizer.YOUTUBE_SHORT_WIDTH, 
                                                video_resizer.YOUTUBE_SHORT_HEIGHT)
    
    audio_extractor = AudioExtractor(INPUT_FILE_PATH,
                                    AUDIO_EXTRACTIONS_PATH)
    
    audio_extraction = audio_extractor.extract_mp3_from_mp4(original_video)
    
    
    # Transcribe the audio file
    # chunk into time segments - for now 8 seconds
    transcriber = Transcriber(AUDIO_EXTRACTIONS_PATH)
    chunk_array = transcriber.run_transcription(audio_extraction, 8)
    

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
                             OUTPUT_FILE_PATH,
                             IMAGE_2_VIDEOS_FILE_PATH)
    
    final_video = media_adder.add_videos_to_original_clip(original_clip=resized_video,
                                       videos=video_data,
                                       original_clip_width=media_adder.YOUTUBE_SHORT_WIDTH,
                                       original_clip_height=media_adder.YOUTUBE_SHORT_HALF_HEIGHT * 2,
                                       overlay_zone_width=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_WIDTH,
                                       overlay_zone_height=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_HEIGHT,
                                       overlay_zone_x=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_X,
                                       overlay_zone_y=media_adder.YOUTUBE_SHORT_OVERLAY_ZONE_Y)

    print("Finished adding videos to original clip")
    
    audioAdder = AudioAdder(OUTPUT_FILE_PATH, AUDIO_EXTRACTIONS_PATH)

    audioAdder.combine_video_audio(final_video, audio_extraction)
    

# make a function that takes in an mp4 video and an mp3 audio file and combines them    
    
# audioAdder = AudioAdder(OUTPUT_FILE_PATH, AUDIO_EXTRACTIONS_PATH)

# audioAdder.combine_video_audio("JordanClip.mp4_6.mp4", "JordanClip.mp3")
# print("I worked")



# creator = ImageToVideoCreator(IMAGE_FILE_PATH,
#                               IMAGE_2_VIDEOS_FILE_PATH)    
    
 
 
main()
    
    
    
