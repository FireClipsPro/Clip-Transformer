from VideoEditor import MediaAdder, VideoResizer, VideoClipper, HeadTrackingCropper, WatermarkAdder, ImageSpacer, PauseRemover, SoundEffectAdder
from content_generation import ImageToVideoCreator, DALL_E, ImageGetter, GoogleImagesAPI, ImageClassifier, ImageEvaluator, FullScreenImageSelector
from text_analyzer import SentenceSubjectAnalyzer, TranscriptAnalyzer, OpenaiApi
from Transcriber import WhisperTranscriber, AudioExtractor
from file_organisation import FileDeleter, FinishedVideoSorter
from video_downloader import YoutubeVideoDownloader
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

def main():
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    raw_videos = get_raw_videos()
    print(raw_videos)
    
    video_clipper = VideoClipper(input_video_file_path=directories.RAW_VIDEO_FOLDER,
                                 output_file_path=directories.INPUT_FOLDER)
    
    audio_extractor = AudioExtractor(directories.INPUT_FOLDER,
                                     directories.AUDIO_EXTRACTIONS_FOLDER)

    transcriber = WhisperTranscriber(directories.AUDIO_EXTRACTIONS_FOLDER, directories.TRANSCRIPTS_FOLDER)
    
    pause_remover = PauseRemover(directories.INPUT_FOLDER, directories.RESIZED_FOLDER)
    
    head_tracker = HeadTrackingCropper(directories.RESIZED_FOLDER,
                                       directories.RESIZED_FOLDER)
    
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

    subtitle_adder = SubtitleAdder(input_folder_path=directories.VIDEOS_WITH_OVERLAYED_MEDIA_PATH,
                                   output_folder_path=directories.WITH_SUBTITLES_FOLDER)
    
    watermark_adder = WatermarkAdder(watermark_folder=directories.WATERMARKS_FOLDER,
                                     input_video_folder=directories.WITH_SUBTITLES_FOLDER,
                                     output_video_folder=directories.WATERMARKED_VIDEOS_FOLDER,
                                     presets=presets)

    music_adder = MusicAdder(music_file_paths=directories.MUSIC_CATEGORY_PATH_DICT,
                        input_video_folder=directories.WATERMARKED_VIDEOS_FOLDER,
                        ouput_video_folder=directories.FINISHED_VIDEOS_FOLDER,
                        music_categories=directories.MUSIC_CATEGORY_PATH_DICT)
    
    finished_video_sorter = FinishedVideoSorter(directories.FINISHED_VIDEOS_FOLDER)

    for raw_video in raw_videos:
        print(str(raw_video['raw_video_name']) + ' is being processed')
        theme = presets.themes[raw_video['preset']]
        
        clipped_video = video_clipper.clip_video(raw_video['raw_video_name'],
            raw_video['start_time'],
            raw_video['end_time'])
        
        audio_extraction_file_name = audio_extractor.extract_mp3_from_mp4(clipped_video['file_name'])
        
        transcription = transcriber.transcribe(audio_extraction_file_name,
            theme['CENSOR_PROFANITY'])
        
        if transcription == None:
            continue
        
        clipped_video, transcription['word_segments'] = pause_remover.remove_pauses(clipped_video,
            transcription['word_segments'],
            theme['MAXIMUM_PAUSE_LENGTH'])
        

        clipped_video = head_tracker.crop_video_to_face_center( clipped_video,
            presets.VERTICAL_VIDEO_WIDTH,
            presets.VERTICAL_VIDEO_HEIGHT)

        
        clipped_video = transcription_analyzer.get_clip_info(clipped_video,
            transcription,
            raw_video['raw_video_name'],
            theme['MUSIC_CATEGORY_OPTIONS'])
        
        query_list = sentence_analyzer.process_transcription(transcription['word_segments'],
            transcription['word_segments'][-1]['end'],
            theme['SECONDS_PER_PHOTO'],
            clipped_video['transcription_info']['descriptions'],
            clipped_video['file_name'])
        
        if theme["WANTS_IMAGES"]:
            
            query_list = image_spacer.add_spacing_to_images(query_list,
                time_between_images=theme["TIME_BETWEEN_IMAGES"])
            
            video_with_sound_effects = sound_effect_adder.add_sounds_to_images(images=query_list,
                video=clipped_video,
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
                theme['OVERLAY_ZONE_HEIGHT'],
                theme['ZOOM_SPEED'])
            
            video_with_media = media_adder.add_videos_to_original_clip(original_clip=video_with_sound_effects,
                videos=video_data,
                original_clip_width=presets.VERTICAL_VIDEO_WIDTH,
                original_clip_height=presets.VERTICAL_VIDEO_HEIGHT * 2,
                overlay_zone_top_left=theme["OVERLAY_ZONE_TOP_LEFT"],
                overlay_zone_width=theme["OVERLAY_ZONE_WIDTH"],
                overlay_zone_height=theme["OVERLAY_ZONE_HEIGHT"])
        else:
            subtitle_adder.input_folder_path = head_tracker.output_folder_path
    
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

        watermarked_video = watermark_adder.add_watermark(image_file_name=theme['WATERMARK'],
            video_file_name=video_with_media['file_name'],
            location=theme['WATERMARK_LOCATION'])
        
        video_with_music_name = music_adder.add_music_to_video_by_category(music_category=clipped_video['transcription_info']['category'],
            video_name=watermarked_video,
            output_video_name=clipped_video['time_string'] + '_' + clipped_video['transcription_info']['title'],
            video_length=clipped_video['end_time_sec'],
            music_category_options=theme['MUSIC_CATEGORY_OPTIONS'],
            background_music_volume=theme["BACKGROUND_MUSIC_VOLUME"])
        
        video_clipper.output_file_path = directories.FINISHED_VIDEOS_FOLDER
        video_clipper.input_video_folder_path = directories.FINISHED_VIDEOS_FOLDER
        video_clipper.clip_video(video_with_music_name,
                                 0,
                                 clipped_video['end_time_sec'])
        video_clipper.input_video_folder_path = directories.RAW_VIDEO_FOLDER
        video_clipper.output_file_path = directories.INPUT_FOLDER
        
        finished_video_sorter.sort_video(raw_video['raw_video_name'], video_with_music_name)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def remove_line_of_input_info():
    with open(directories.INPUT_INFO_FILE, 'r') as file:
        lines = file.readlines()

    with open(directories.INPUT_INFO_FILE, 'w') as file:
        file.writelines(lines[1:])  # Skip the first line


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_raw_videos():
    raw_videos = []
    with open(directories.INPUT_INFO_FILE, 'r') as csv_file:
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
            
            raw_videos.append({'preset': str(line[0]),
                                'link': str(line[1]),
                                'start_time': str(line[2]),
                                'end_time': str(line[3])})
            
            lines_read += 1
    
    downloader = YoutubeVideoDownloader(output_folder=directories.RAW_VIDEO_FOLDER,
                                        downloaded_videos_file=directories.DOWNLOADED_VIDEOS_FILE)
    raw_videos = downloader.download_videos(raw_videos)
    
    return raw_videos

 
main()