from VideoEditor import MediaAdder, ImageSpacer, SoundEffectAdder, BackgroundCreator, IntroAdder, WatermarkAdder
from content_generation import TextToSpeech, ImageToVideoCreator, DALL_E, ImageGetter, GoogleImagesAPI, ImageClassifier, ImageEvaluator
from Transcriber import CloudTranscriber
from text_analyzer import ImageQueryCreator, TranscriptAnalyzer, OpenaiApi
from music_adder import MusicAdder
from subtitle_adder import SubtitleAdder
import configuration.directories as directories
import configuration.video_maker_presets as presets
import boto3
from services import S3
import logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def main():
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    audio_files = get_audio_files()
    print(audio_files)
    
    text_2_speech = TextToSpeech(audio_folder=directories.VM_AUDIO_INPUT)
    
    blank_video_creator = BackgroundCreator(input_audio_folder=directories.VM_AUDIO_INPUT,
                                            output_video_folder=directories.VM_BLANK_VIDEOS,
                                            background_media_folder=directories.VM_BACKGROUNDS)
    
    transcriber = CloudTranscriber(s3=S3(boto3.client('s3')),
                                   output_folder=directories.VM_TRANSCRIPTS,
                                   input_audio_folder=directories.VM_AUDIO_INPUT)
    
    music_adder = MusicAdder(music_folder=directories.VM_SONGS,
                             input_video_folder=directories.VM_BLANK_VIDEOS,
                             output_video_folder=directories.VM_VIDEOS_WITH_MUSIC,
                             music_categories=directories.MUSIC_CATEGORY_PATH_DICT)
                             
    openai_api = OpenaiApi()

    transcription_analyzer = TranscriptAnalyzer(video_info_folder=directories.VM_VIDEO_INFO,
                                                music_category_list=directories.MUSIC_CATEGORY_PATH_DICT,
                                                openai_api=openai_api)

    sentence_analyzer = ImageQueryCreator(queries_folder_path=directories.QUERY_FOLDER,
                                          openai_api=openai_api)
    
    image_spacer = ImageSpacer()
    
    sound_effect_adder = SoundEffectAdder(image_sounds_folder=directories.IMAGE_SOUNDS_FOLDER,
                                          video_input_folder=directories.VM_BLANK_VIDEOS,
                                          output_folder=directories.VM_BLANK_VIDEOS)
    
    # image_classifier = ImageClassifier(image_folder_path=directories.VM_IMAGES)
    
    image_evaluator = ImageEvaluator(image_file_path=directories.VM_IMAGES)

    image_scraper = GoogleImagesAPI(image_file_path=directories.VM_IMAGES,
                                    image_evaluator=image_evaluator)
    
    dall_e = DALL_E()
    
    image_getter = ImageGetter(directories.VM_IMAGES,
                               image_scraper=image_scraper,
                               image_evaluator=image_evaluator,
                               image_generator=dall_e)

    image_to_video_creator = ImageToVideoCreator(image_folder=directories.VM_IMAGES,
                                                 image_2_videos_folder=directories.VM_VIDEOS_MADE_FROM_IMAGES,
                                                 image_evaluator=image_evaluator)

    media_adder = MediaAdder(input_video_folder=directories.VM_VIDEOS_WITH_MUSIC,
                    media_added_vidoes_file_path=directories.VM_VIDEOS_WITH_MEDIA,
                    image_videos_file_path=directories.VM_VIDEOS_MADE_FROM_IMAGES,
                    final_output_file_path=directories.VM_VIDEOS_WITH_MEDIA)

    watermark_adder = WatermarkAdder(watermark_folder=directories.VM_WATERMARKS,
                                     input_video_folder=directories.VM_VIDEOS_WITH_MEDIA,
                                     output_video_folder=directories.VM_WATERMARKED_VIDEOS,
                                     presets=presets)
    
    subtitle_adder = SubtitleAdder(input_folder_path=directories.VM_WATERMARKED_VIDEOS,
                                   output_folder_path=directories.VM_SUBTITLED_VIDEOS)
    
    
    # intro_adder = IntroAdder(intro_video_folder=directories.VM_INTRO_VIDOES,
    #                          video_folder=directories.VM_SUBTITLED_VIDEOS,
    #                          output_folder=directories.VM_FINISHED_VIDEOS)

    # loop through the files
    for audio_file in audio_files:
        print(str(audio_file['file_name']) + ' is being processed')
        preset = presets.preset[audio_file['preset']]
        
        if audio_file['file_name'].endswith('.txt'):
            audio_file['file_name'] = create_audio_file(text_2_speech, audio_file, preset)         
        
        # create a blank video that is 1920 x 1080 that is the same length of the mp3 file
        blank_video = blank_video_creator.create_horizontal(audio_file_name=audio_file['file_name'],
                                                             background_media=preset['AUDIO_ONLY_BACKGROUND_MEDIA'],
                                                             background_color=preset['AUDIO_ONLY_BACKGROUND_COLOR'],
                                                             width=preset['VIDEO_WIDTH'],
                                                             height=preset['VIDEO_HEIGHT'])
        
        logging.info('blank video created: ' + str(blank_video))
        music_adder.add_music_to(music_file_name=preset['SONG'],
                                 video_name=blank_video['file_name'],
                                 output_video_name=blank_video['file_name'],
                                 video_length=blank_video['end_time_sec'],
                                 background_music_volume=0.75)

        transcription = transcriber.transcribe(audio_file['file_name'])
        
        if transcription == None:
            continue
        
        description_list = transcription_analyzer.get_info_for_entire_pod(video_file_name=audio_file['file_name'],
                                                                          transcription=transcription,
                                                                          podcast_title=audio_file['file_name'])
        
        query_list = sentence_analyzer.process_transcription(transcription=transcription['word_segments'],
                                        transcription_length_sec=transcription['word_segments'][-1]['end'],
                                        seconds_per_query=preset['SECONDS_PER_PHOTO'],
                                        descriptions=description_list,
                                        output_file_name=blank_video['file_name'],
                                        wants_free_images=preset['WANTS_ROYALTY_FREE_IMAGES'])
        
        query_list = image_spacer.add_spacing_to_images(query_list,
                                                        time_between_images=preset["TIME_BETWEEN_IMAGES"])
        
        video_with_sound_effects = sound_effect_adder.add_sounds_to_images(images=query_list,
                                                                            video=blank_video,
                                                                            wants_sounds=preset['WANTS_SOUND_EFFECTS'])
        
        image_scraper.wants_royalty_free = preset['WANTS_ROYALTY_FREE_IMAGES']
        time_stamped_images = image_getter.get_images(query_list=query_list, wants_to_use_dall_e=preset['WANTS_DALL_E_IMAGES'])
        
        # print the _time_stamped_images array
        print(time_stamped_images)
        
        video_data = image_to_video_creator.convert_to_videos(time_stamped_images,
            preset['IMAGE_BORDER_COLOR(S)'],
            preset['OVERLAY_ZONE_WIDTH'],
            preset['OVERLAY_ZONE_HEIGHT'],
            preset['ZOOM_SPEED'])
        
        logging.info(str(video_with_sound_effects))
        
        #original clip needs 'file_name', 'end_time_sec' and 'start_time_sec' added to it
        video_with_media = media_adder.add_media_to_video(original_clip=video_with_sound_effects,
            videos=video_data,
            original_clip_width=presets.VERTICAL_VIDEO_WIDTH,
            original_clip_height=presets.VERTICAL_VIDEO_HEIGHT * 2,
            overlay_zone_top_left=preset['OVERLAY_ZONE_TOP_LEFT'],
            overlay_zone_width=preset['OVERLAY_ZONE_WIDTH'],
            overlay_zone_height=preset['OVERLAY_ZONE_HEIGHT'])
        
        watermarked_video = watermark_adder.add_watermark(image_file_name=preset['WATERMARK'],
            video_file_name=video_with_media['file_name'],
            location=preset['WATERMARK_LOCATION'],
            wants_watermark=preset['WANTS_WATERMARK'])
    
        video_with_subtitles_name = subtitle_adder.add_subtitles_to_video(video_file_name=watermarked_video,
            transcription=transcription['word_segments'],
            output_file_name='sub_' + video_with_media['file_name'],
            font_size=preset['FONT_SIZE'],
            font_name=preset['FONT'],
            outline_color=preset['FONT_OUTLINE_COLOR'],
            outline_width=preset['FONT_OUTLINE_WIDTH'],
            font_color=preset['FONT_COLOR'],
            all_caps=preset['ALL_CAPS'],
            punctuation=preset['PUNCTUATION'],
            y_percent=preset['Y_PERCENT_HEIGHT_OF_SUBTITLE'],
            number_of_characters_per_line=preset['NUMBER_OF_CHARACTERS_PER_LINE'])
        
        # video_with_intro = intro_adder.add_video_intro(video_file_name=video_with_subtitles_name,
        #                                                intro_file_name=preset['INTRO_FILE'])
        
        logging.info('FINISHED!!!' + video_with_subtitles_name + " Congrats you amazing guy you!")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def create_audio_file(text_2_speech,
                      audio_file,
                      preset):
    audio_file_name = audio_file['file_name'][:-4] + '.mp3'
    text_file_path = directories.VM_TEXT_INPUT + audio_file['file_name']
    
    #read the .txt file into a string
    with open(text_file_path, 'r') as file:
        text = file.read()
            
    text_2_speech.generate_audio(audio_file_name=audio_file_name,
                                 text=text,
                                 voice=preset['VOICE'])
    
    return audio_file_name
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