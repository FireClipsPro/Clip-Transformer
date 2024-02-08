from VideoEditor import MediaAdder, ImageSpacer, SoundEffectAdder, BackgroundCreator, IntroAdder, WatermarkAdder
from content_generation import ImageToVideoCreator, DALL_E, ImageGetter, GoogleImagesAPI, ImageClassifier, ImageEvaluator, FullScreenImageSelector
from Transcriber import WhisperTranscriber, AudioExtractor
from text_analyzer import ImageQueryCreator, TranscriptAnalyzer, OpenaiApi
from file_organisation import FileDeleter, FinishedVideoSorter
from music_adder import MusicAdder
from subtitle_adder import SubtitleAdder
import configuration.directories as directories
import configuration.video_maker_presets as presets
import os
import math
import logging
import csv
import time
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def main():
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    audio_files = get_audio_files()
    print(audio_files)
    
    blank_video_creator = BackgroundCreator(input_audio_folder=directories.VM_AUDIO_INPUT,
                                            output_video_folder=directories.VM_BLANK_VIDEOS,
                                            background_media_folder=directories.VM_BACKGROUNDS)
    
    audio_extractor = AudioExtractor(input_file_path=directories.VM_AUDIO_INPUT,
                                     audio_extraction_path=directories.VM_AUDIO_EXTRACTIONS)

    transcriber = WhisperTranscriber(audio_files_path=directories.VM_AUDIO_EXTRACTIONS, 
                                     transcripts_folder=directories.VM_TRANSCRIPTS)
    
    openai_api = OpenaiApi()

    transcription_analyzer = TranscriptAnalyzer(video_info_folder=directories.VM_VIDEO_INFO,
                                                music_cat_list=directories.MUSIC_CATEGORY_PATH_DICT,
                                                openai_api=openai_api)

    sentence_analyzer = ImageQueryCreator(queries_folder_path=directories.QUERY_FOLDER,
                                          openai_api=openai_api)
    
    image_spacer = ImageSpacer()
    
    sound_effect_adder = SoundEffectAdder(image_sounds_folder=directories.IMAGE_SOUNDS_FOLDER,
                                          video_input_folder=directories.VM_BLANK_VIDEOS,
                                          output_folder=directories.VM_BLANK_VIDEOS)
    
    image_classifier = ImageClassifier(image_folder_path=directories.VM_IMAGES)
    
    image_evaluator = ImageEvaluator(image_file_path=directories.VM_IMAGES)

    image_scraper = GoogleImagesAPI(image_file_path=directories.VM_IMAGES,
                                    image_classifier=image_classifier,
                                    image_evaluator=image_evaluator)
    
    dall_e = DALL_E(output_folder=directories.VM_IMAGES,
                    dalle_prompt_folder=directories.GENERATED_PROMPTS_FOLDER)
    
    image_getter = ImageGetter(directories.VM_IMAGES,
                               image_scraper=image_scraper,
                               image_evaluator=image_evaluator,
                               image_generator=dall_e)

    image_to_video_creator = ImageToVideoCreator(image_folder=directories.VM_IMAGES,
                                                 image_2_videos_folder=directories.VM_VIDEOS_MADE_FROM_IMAGES,
                                                 image_evaluator=image_evaluator)

    media_adder = MediaAdder(input_video_folder=directories.VM_BLANK_VIDEOS,
                    media_added_vidoes_file_path=directories.VM_VIDEOS_WITH_MEDIA,
                    image_videos_file_path=directories.VM_VIDEOS_MADE_FROM_IMAGES,
                    final_output_file_path=directories.VM_VIDEOS_WITH_MEDIA)

    watermark_adder = WatermarkAdder(watermark_folder=directories.VM_WATERMARKS,
                                     input_video_folder=directories.VM_VIDEOS_WITH_MEDIA,
                                     output_video_folder=directories.VM_WATERMARKED_VIDEOS,
                                     presets=presets)
    
    subtitle_adder = SubtitleAdder(input_folder_path=directories.VM_WATERMARKED_VIDEOS,
                                   output_folder_path=directories.VM_FINISHED_VIDEOS)
    
    
    # intro_adder = IntroAdder(intro_vid_folder=directories.INTRO_VIDEOS,
    #                          video_folder=directories.WITH_SUBTITLES_FOLDER,
    #                          output_folder=directories.FINISHED_AUD2VID_FOLDER)

    # loop through the files
    for audio_file in audio_files:
        print(str(audio_file['file_name']) + ' is being processed')
        theme = presets.themes[audio_file['preset']]
        
        # create a blank video that is 1920 x 1080 that is the same length of the mp3 file
        blank_video = blank_video_creator.create_horizontal(audio_file_name=audio_file['file_name'],
                                                             background_media=theme['AUDIO_ONLY_BACKGROUND_MEDIA'],
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
                                        output_file_name=blank_video['file_name'],
                                        wants_free_images=theme['WANTS_ROYALTY_FREE_IMAGES'])
        
        query_list = image_spacer.add_spacing_to_images(query_list,
                                                        time_between_images=theme["TIME_BETWEEN_IMAGES"])
        
        video_with_sound_effects = sound_effect_adder.add_sounds_to_images(images=query_list,
                                                                            video=blank_video,
                                                                            wants_sounds=theme['WANTS_SOUND_EFFECTS'])
        
        image_scraper.wants_royalty_free = theme['WANTS_ROYALTY_FREE_IMAGES']
        time_stamped_images = image_getter.get_images(query_list=query_list, wants_to_use_dall_e=theme['WANTS_DALL_E_IMAGES'])
        
        # where images could not be found, DALL-E will be used to generate images
        time_stamped_images = dall_e.create_missing_images(time_stamped_images)
        
        # print the _time_stamped_images array
        print(time_stamped_images)
        
        video_data = image_to_video_creator.convert_to_videos(time_stamped_images,
            theme["IMAGE_BORDER_COLOR(S)"],
            theme['OVERLAY_ZONE_WIDTH'],
            theme['OVERLAY_ZONE_HEIGHT'],
            theme['ZOOM_SPEED'])
        
        logging.info(str(video_with_sound_effects))
        
        #original clip needs 'file_name', 'end_time_sec' and 'start_time_sec' added to it
        video_with_media = media_adder.add_videos_to_original_clip(original_clip=video_with_sound_effects,
            videos=video_data,
            original_clip_width=presets.VERTICAL_VIDEO_WIDTH,
            original_clip_height=presets.VERTICAL_VIDEO_HEIGHT * 2,
            overlay_zone_top_left=theme["OVERLAY_ZONE_TOP_LEFT"],
            overlay_zone_width=theme["OVERLAY_ZONE_WIDTH"],
            overlay_zone_height=theme["OVERLAY_ZONE_HEIGHT"])
        
        watermarked_video = watermark_adder.add_watermark(image_file_name=theme['WATERMARK'],
            video_file_name=video_with_media['file_name'],
            location=theme['WATERMARK_LOCATION'],
            wants_watermark=theme['WANTS_WATERMARK'])
    
        video_with_subtitles_name = subtitle_adder.add_subtitles_no_grouping(video_file_name=watermarked_video,
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
            number_of_characters_per_line=theme["NUMBER_OF_CHARACTERS_PER_LINE"])
        
        # video_with_intro = intro_adder.add_video_intro(video_file_name=video_with_subtitles_name,
        #                                                intro_file_name=theme['INTRO_FILE'])
        
        logging.info('FINISHED:' + video_with_subtitles_name)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_audio_files():
    audio_files = []
    with open(directories.VM_INPUT_FILE, 'r') as csv_file:
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