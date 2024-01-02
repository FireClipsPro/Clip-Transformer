from VideoEditor import MediaAdder, VideoResizer, VideoClipper, HeadTrackingCropper, ImageSpacer, PauseRemover, SoundEffectAdder
from content_generation import ImageScraper, ImageToVideoCreator, DALL_E, ImageGetter, GoogleImagesAPI, ImageClassifier, ImageEvaluator, FullScreenImageSelector
from text_analyzer import SentenceSubjectAnalyzer, TranscriptAnalyzer, OpenaiApi
from Transcriber import WhisperTranscriber, AudioExtractor, YoutubeTranscriptionApi
from file_organisation import FileDeleter, FinishedVideoSorter
from video_downloader import YoutubeVideoDownloader
from music_adder import MusicAdder
from subtitle_adder import SubtitleAdder
from clip_finder import ClipLenghtReducer, HighlightFinder
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
    full_pods = get_full_pods()
    logging.info(full_pods)
    
    openai_api = OpenaiApi()
    
    yt_transcript_api = YoutubeTranscriptionApi()
    
    highlight_finder = HighlightFinder(openai_api=openai_api,
                                       hooks_folder_path=directories.HOOKS_FOLDER,
                                       clip_end_folder_path=directories.CLIP_END_FOLDER)
    
    video_clipper = VideoClipper(input_video_file_path=directories.FULL_POD_FOLDER,
                                 output_file_path=directories.POTENTIAL_CLIP_FOLDER)
    
    audio_extractor = AudioExtractor(directories.POTENTIAL_CLIP_FOLDER,
                                     directories.AUDIO_EXTRACTIONS_FOLDER)

    transcriber = WhisperTranscriber(directories.AUDIO_EXTRACTIONS_FOLDER,
                                     directories.TRANSCRIPTS_FOLDER)
    
    pause_remover = PauseRemover(directories.POTENTIAL_CLIP_FOLDER, 
                                 directories.POTENTIAL_CLIP_FOLDER)
    
    clip_length_reducer = ClipLenghtReducer(openai_api=openai_api,
                                            input_clip_folder_path=directories.POTENTIAL_CLIP_FOLDER,
                                            output_clip_folder_path=directories.RESIZED_FOLDER)
    
    #clip length reducer
    head_tracker = HeadTrackingCropper(directories.RESIZED_FOLDER,
                                       directories.RESIZED_FOLDER)

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

    music_adder = MusicAdder(music_file_paths=directories.MUSIC_CATEGORY_PATH_DICT,
                        video_files_path=directories.WITH_SUBTITLES_FOLDER,
                        output_path=directories.FINISHED_VIDEOS_FOLDER,
                        music_categories=directories.MUSIC_CATEGORY_PATH_DICT)
    
    finished_video_sorter = FinishedVideoSorter(directories.FINISHED_VIDEOS_FOLDER)
    
    for pod in full_pods:
        # download video from youtube and get the highlights
        yt_transcript = yt_transcript_api.get_transcription(pod['link'])
        clips = highlight_finder.get_highlights(video_id=pod['raw_video_name'],
                                                transcript=yt_transcript)
        
        # loop through the files
        for clip in clips:
            print(str(clip['raw_video_name']) + ' is being processed')
            theme = presets.themes[pod['preset']]
            
            clipped_video = video_clipper.clip_video(pod['raw_video_name'],
                                                     clip['start_time'],
                                                     clip['end_time'])
            
            audio_extraction_file_name = audio_extractor.extract_mp3_from_mp4(clipped_video['file_name'])
            
            transcript = transcriber.transcribe(audio_extraction_file_name,
                                                theme['CENSOR_PROFANITY'])
            
            transcript, reduced_length_clip = clip_length_reducer.reduce(transcript, clipped_video['file_name'])
            clipped_video['file_name'] = reduced_length_clip['file_name']
            
            if transcript == None:
                continue
            
            clipped_video, transcript['word_segments'] = pause_remover.remove_pauses(clipped_video,
                                                                        transcript['word_segments'],
                                                                        theme['MAXIMUM_PAUSE_LENGTH'])
            
            clipped_video = head_tracker.crop_video_to_face_center( clipped_video,
                                            presets.VERTICAL_VIDEO_WIDTH,
                                            presets.VERTICAL_VIDEO_HEIGHT)
            
            clipped_video = transcription_analyzer.get_info(clipped_video,
                                                            transcript,
                                                            clip['raw_video_name'],
                                                            theme['MUSIC_CATEGORY_OPTIONS'])
            
            query_list = sentence_analyzer.process_transcription(transcript['word_segments'],
                                            transcript['word_segments'][-1]['end'],
                                            theme['SECONDS_PER_PHOTO'],
                                            clipped_video['transcription_info']['description'],
                                            clipped_video['file_name'])
            
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
                                                                theme['OVERLAY_ZONE_HEIGHT'])
            
            video_with_media = media_adder.add_videos_to_original_clip(original_clip=video_with_sound_effects,
                                            videos=video_data,
                                            original_clip_width=presets.VERTICAL_VIDEO_WIDTH,
                                            original_clip_height=presets.VERTICAL_VIDEO_HEIGHT * 2,
                                            overlay_zone_top_left=theme["OVERLAY_ZONE_TOP_LEFT"],
                                            overlay_zone_width=theme["OVERLAY_ZONE_WIDTH"],
                                            overlay_zone_height=theme["OVERLAY_ZONE_HEIGHT"])
        
            video_with_subtitles_name = subtitle_adder.add_subtitles_to_video(video_file_name=video_with_media['file_name'],
                                                        transcription=transcript['word_segments'],
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

            video_with_music_name = music_adder.add_music_to_video(music_category=clipped_video['transcription_info']['category'],
                                            video_name=video_with_subtitles_name,
                                            output_video_name=clipped_video['time_string'] + '_' + clipped_video['transcription_info']['title'],
                                            video_length=clipped_video['end_time_sec'],
                                            music_category_options=theme['MUSIC_CATEGORY_OPTIONS'],
                                            background_music_volume=theme["BACKGROUND_MUSIC_VOLUME"])
            
            video_clipper.output_file_path = directories.FINISHED_VIDEOS_FOLDER
            video_clipper.input_video_folder_path = directories.FINISHED_VIDEOS_FOLDER
            video_clipper.clip_video(video_with_music_name,
                                    0,
                                    clipped_video['end_time_sec'])
            video_clipper.input_video_folder_path = directories.FULL_POD_FOLDER
            video_clipper.output_file_path = directories.POTENTIAL_CLIP_FOLDER
            
            finished_video_sorter.sort_video(clip['raw_video_name'], video_with_music_name)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_full_pods():
    full_pods = []
    with open(directories.INPUT_YOUTUBE_LINK, 'r') as csv_file:
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
            
            full_pods.append({'preset': str(line[0]),
                                'link': str(line[1])})
            
            lines_read += 1
    
    downloader = YoutubeVideoDownloader(output_folder=directories.FULL_POD_FOLDER,
                                        downloaded_videos_file=directories.DOWNLOADED_VIDEOS_FILE)
    full_pods = downloader.download_videos(full_pods)
    
    return full_pods

 
main()