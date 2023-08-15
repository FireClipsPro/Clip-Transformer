from VideoEditor import MediaAdder, ImageSpacer, SoundEffectAdder, BlankVideoCreator
from content_generation import ImageToVideoCreator, DALL_E, ImageGetter, GoogleImagesAPI, ImageClassifier, ImageEvaluator, FullScreenImageSelector
from text_analyzer import SentenceSubjectAnalyzer, TranscriptAnalyzer, OpenaiApi
from Transcriber import WhisperTranscriber, AudioExtractor
from file_organisation import FileDeleter, FinishedVideoSorter
from music_adder import MusicAdder
from subtitle_adder import SubtitleAdder
import configuration.directories as directories
import configuration.presets as presets
import os
import math
import logging
import csv
import time
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

VERTICAL_VIDEO_HEIGHT = 1920
VERTICAL_VIDEO_WIDTH = 1080
HEAD_TRACKING_ENABLED = True
SECONDS_PER_PHOTO = 6
PERECENT_OF_IMAGES_TO_BE_FULLSCREEN = 0.3
MAXIMUM_PAUSE_LENGTH = 0.5
TIME_BETWEEN_IMAGES = 1.5
Y_PERCENT_HEIGHT_OF_SUBTITLE = 60
SUBTITLE_DURATION = 1
DURATION_OF_FULL_SCREEN_IMAGES = 3

def main():
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    audio_files = get_audio_files()
    print(audio_files)
    
    blank_video_creator = BlankVideoCreator(audio_folder=directories.AUDIO_EXTRACTIONS_FOLDER,
                                            video_folder=directories.RESIZED_FOLDER,
                                            background_image_folder=directories.BACKGROUND_FOLDER)
    
    audio_extractor = AudioExtractor(directories.INPUT_FOLDER,
                                     directories.AUDIO_EXTRACTIONS_FOLDER)

    transcriber = WhisperTranscriber(directories.AUDIO_EXTRACTIONS_FOLDER, 
                                     directories.TRANSCRIPTS_FOLDER)
    
    openai_api = OpenaiApi()

    transcription_analyzer = TranscriptAnalyzer(directories.VIDEO_INFO_FOLDER,
                                                directories.MUSIC_CATEGORY_PATH_DICT,
                                                openai_api)

    sentence_analyzer = SentenceSubjectAnalyzer(directories.QUERY_FOLDER,
                                                openai_api)
    
    image_spacer = ImageSpacer()
    
    sound_effect_adder = SoundEffectAdder(directories.IMAGE_SOUNDS_FOLDER,
                                          directories.RESIZED_FOLDER,
                                          directories.RESIZED_FOLDER)
    
    image_classifier = ImageClassifier(directories.IMAGE_FOLDER)
    
    image_evaluator = ImageEvaluator(directories.IMAGE_FOLDER)

    image_scraper = GoogleImagesAPI(directories.IMAGE_FOLDER,
                                    image_classifier,
                                    image_evaluator)
    
    image_getter = ImageGetter(directories.IMAGE_FOLDER,
                               image_scraper,
                               image_evaluator)

    dall_e = DALL_E(directories.IMAGE_FOLDER,
                    directories.GENERATED_PROMPTS_FOLDER)
    
    fullscreen_image_selector = FullScreenImageSelector(directories.IMAGE_FOLDER,
                                                        image_evaluator=image_evaluator)

    image_to_video_creator = ImageToVideoCreator(directories.IMAGE_FOLDER,
                                                 directories.IMAGE_2_VIDEOS_FOLDER,
                                                 image_evaluator=image_evaluator)

    media_adder = MediaAdder(directories.RESIZED_FOLDER,
                    directories.VIDEOS_WITH_OVERLAYED_MEDIA_PATH,
                    directories.IMAGE_2_VIDEOS_FOLDER,
                    directories.VIDEOS_WITH_OVERLAYED_MEDIA_PATH)

    subtitle_adder = SubtitleAdder(directories.VIDEOS_WITH_OVERLAYED_MEDIA_PATH,
                                    directories.WITH_SUBTITLES_FOLDER)

    # loop through the files
    for audio_file in audio_files:
        print(str(audio_file['file_name']) + ' is being processed')
        theme = presets.themes[audio_file['preset']]
        
        # create a blank video that is 1920 x 1080 that is the same length of the mp3 file
        blank_video = blank_video_creator.create_horizontal(audio_file_name=audio_file['file_name'],
                                                             background_media_name=theme['AUDIO_ONLY_BACKGROUND_MEDIA'],
                                                             background_color=theme['AUDIO_ONLY_BACKGROUND_COLOR'],
                                                             width=presets.HORIZONTAL_VIDEO_WIDTH,
                                                             height=presets.HORIZONTAL_VIDEO_HEIGHT)
        
        audio_file['file_name'] = audio_extractor.extract_mp3_from_mp4(audio_file['file_name'])
        
        print('audio_file is: ' + str(audio_file))
        transcription = transcriber.transcribe(audio_file['file_name'],
                                               theme['CENSOR_PROFANITY'])
        
        if transcription == None:
            continue
        
        description_list = transcription_analyzer.get_info_for_entire_pod(video_file_name=audio_file['file_name'],
                                                                          transcription=transcription,
                                                                          podcast_title=audio_file['file_name'])
        
        query_list = sentence_analyzer.process_transcription(transcription=transcription['word_segments'],
                                        transcription_length_sec=transcription['word_segments'][-1]['end'],
                                        seconds_per_query=theme['SECONDS_PER_PHOTO'],
                                        descriptions=description_list,
                                        output_file_name=blank_video['file_name'])
        
        query_list = image_spacer.add_spacing_to_images(query_list,
                                                        time_between_images=theme["TIME_BETWEEN_IMAGES"])
        
        video_with_sound_effects = sound_effect_adder.add_sounds_to_images(images=query_list,
                                                                            video=blank_video,
                                                                            wants_sounds=theme['WANTS_SOUND_EFFECTS'])
        
        time_stamped_images = image_getter.get_images(query_list)
        
        # where images could not be found, DALL-E will be used to generate images
        time_stamped_images = dall_e.generate_images(time_stamped_images)
        
        # print the _time_stamped_images array
        print(time_stamped_images)
        
        # add fullscreenimageselector here
        time_stamped_images = fullscreen_image_selector.choose_fullscreen_images(time_stamped_images,
            presets.VERTICAL_VIDEO_WIDTH,
            presets.VERTICAL_VIDEO_HEIGHT,
            presets.VERTICAL_VIDEO_WIDTH,
            int(presets.VERTICAL_VIDEO_HEIGHT / 2),
            percent_of_images_to_be_fullscreen=theme["PERECENT_OF_IMAGES_TO_BE_FULLSCREEN"],
            fullscreen_duration=theme["DURATION_OF_FULL_SCREEN_IMAGES"])
        
        video_data = image_to_video_creator.convert_to_videos(time_stamped_images,
            theme["IMAGE_BORDER_COLOR(S)"],
            theme['OVERLAY_ZONE_WIDTH'],
            theme['OVERLAY_ZONE_HEIGHT'])
        
        logging.info(str(video_with_sound_effects))
        
        #original clip needs 'file_name', 'end_time_sec' and 'start_time_sec' added to it
        video_with_media = media_adder.add_videos_to_original_clip(original_clip=video_with_sound_effects,
            videos=video_data,
            original_clip_width=presets.VERTICAL_VIDEO_WIDTH,
            original_clip_height=presets.VERTICAL_VIDEO_HEIGHT * 2,
            overlay_zone_top_left=theme["OVERLAY_ZONE_TOP_LEFT"],
            overlay_zone_width=theme["OVERLAY_ZONE_WIDTH"],
            overlay_zone_height=theme["OVERLAY_ZONE_HEIGHT"])
    
        video_with_subtitles_name = subtitle_adder.add_subtitles_to_video(video_file_name=video_with_media['file_name'],
            transcription=transcription['word_segments'],
            output_file_name='sub_' + video_with_media['file_name'],
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
        
        print('video_with_subtitles_name is: ' + video_with_subtitles_name)
    
    

def remove_line_of_input_info():
    with open(directories.INPUT_INFO_FILE, 'r') as file:
        lines = file.readlines()

    with open(directories.INPUT_INFO_FILE, 'w') as file:
        file.writelines(lines[1:])  # Skip the first line


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_audio_files():
    audio_files = []
    with open(directories.AUDIO_TO_VIDEO_INPUT_INFO, 'r') as csv_file:
        lines_read = 0
        for line in csv_file:
            logging.info("line is ________: " + line)
            # skip the first line
            if lines_read == 0:
                logging.info("skipping first line")
                lines_read += 1
                continue
            line = line.strip()
            line = line.split(',')
            
            audio_files.append({'file_name': str(line[0]),
                                'preset': str(line[1])})
            
            lines_read += 1
    
    return audio_files

 
main()