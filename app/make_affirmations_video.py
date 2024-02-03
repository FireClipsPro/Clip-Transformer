from VideoEditor import BackgroundCreator, IntroAdder, WatermarkAdder
from content_generation import TextToSpeech, AffirmationsGenerator, AffirmationsTrackBuilder, IntroCreator, OutroCreator
from text_analyzer import  OpenaiApi
from file_organisation import FileDeleter, FinishedVideoSorter
from music_adder import MusicAdder
from subtitle_adder import SubtitleAdder
from title_generators import AffirmationsTitleGenerator
import configuration.directories as directories
import configuration.manifestation_presets as presets
import logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def main():
    # read from the csv file in ./media_storage/input_info.csv and parse the data
    # into a list of dictionaries
    prompt = "I want to live in the moment and be calm and happy. I want to be confident in myself."
    
    
    tracks = [{'file_name': 'healing.mp3',
                    'preset': 'molecular',
                    'prompt': prompt}]
    
    openai_api = OpenaiApi()
    
    title_generator = AffirmationsTitleGenerator(openai_api=openai_api)
    
    affirmations_generator = AffirmationsGenerator(openai_api=openai_api,
                                                   affirmations_folder=directories.AFFIRMATION_FOLDER)
    
    text_to_speech = TextToSpeech(audio_folder=directories.AFFIRMATION_FOLDER)
    
    affirmations_track_builder = AffirmationsTrackBuilder(text_to_speech=text_to_speech,
                                                          affirmations_folder=directories.AFFIRMATION_FOLDER,
                                                          output_folder=directories.AFFIRMATION_AUDIO_TRACKS)
    
    
    blank_video_creator = BackgroundCreator(input_audio_folder=directories.AFFIRMATION_AUDIO_TRACKS,
                                            output_video_folder=directories.AFFIRMATION_BLANK_VIDEOS,
                                            background_media_folder=directories.BACKGROUND_FOLDER)

    intro_creator = IntroCreator(text_to_audio=text_to_speech,
                                intro_text_folder=directories.AFFIRMATION_INTRO_TEXT, 
                                intro_audio_folder=directories.AFFIRMATION_INTRO_AUDIO,
                                affirmation_tracks_folder=directories.AFFIRMATION_BLANK_VIDEOS,
                                output_folder=directories.AFFIRMATION_WITH_INTRO,
                                intro_image_folder=directories.AFFIRMATION_IMAGES,
                                animations_folder=directories.AFFIRMATION_VIDEOS,
                                intro_video_folder=directories.AFFIRMATION_INTRO_VIDEOS)
    
    outro_creator = OutroCreator(text_to_audio=text_to_speech,
                                 outro_text_folder=directories.AFFIRMATION_OUTRO_TEXT,
                                 outro_audio_folder=directories.AFFIRMATION_OUTRO_AUDIO,
                                 affirmation_tracks_folder=directories.AFFIRMATION_WITH_INTRO,
                                 output_folder=directories.AFFIRMATION_WITH_OUTRO,
                                 outro_image_folder=directories.AFFIRMATION_IMAGES)        
    
    watermark_adder = WatermarkAdder(watermark_folder=directories.WATERMARKS_FOLDER,
                                     input_video_folder=directories.AFFIRMATION_WITH_OUTRO,
                                     output_video_folder=directories.AFFIRMATION_WATERMARKED,
                                     presets=presets)
    
    subtitle_adder = SubtitleAdder(input_folder_path=directories.AFFIRMATION_WATERMARKED,
                                   output_folder_path=directories.SUBTITLED_AFFIRMATIONS)
    
    music_adder = MusicAdder(music_file_paths=directories.AFFIRMATIONS_MUSIC,
                            input_video_folder=directories.SUBTITLED_AFFIRMATIONS,
                            ouput_video_folder=directories.FINISHED_AFFIRMATIONS,
                            music_categories=None,
                            affirmation_music_folder=directories.AFFIRMATIONS_MUSIC)

    # loop through the files
    for affirmation_track in tracks:
        print(str(affirmation_track['file_name']) + ' is being processed')
        theme = presets.themes[affirmation_track['preset']]
        file_name_base = affirmation_track['file_name']
        
        affirmation_track['file_name'] = title_generator.generate_title(affirmation_track['prompt'])
        
        affirmations = affirmations_generator.generate(
            prompt=affirmation_track['prompt'],
            count=theme['AFFIRMATION_COUNT'],
            filename=file_name_base)
        
        affirmations_track = affirmations_track_builder.build_track(
            affirmations=affirmations,
            affirmations_filename_base=file_name_base,
            output_file_name=file_name_base)
        # affirmations_track = {file_name, length, transcript}
        
        #video = {file_name, start_time_sec, end_time_sec, transcript}
        video = blank_video_creator.create_horizontal(
            audio_file_name=file_name_base,
            background_media=theme['AUDIO_ONLY_BACKGROUND_MEDIA'],
            background_color=theme['AUDIO_ONLY_BACKGROUND_COLOR'],
            width=presets.HORIZONTAL_VIDEO_WIDTH,
            height=presets.HORIZONTAL_VIDEO_HEIGHT)
        video['transcript'] = affirmations_track['transcript']
        
        # video = {file_name, end_time_sec, transcript}
        video['file_name'], video['transcript'] = intro_creator.add_intro_video(
            transcript=affirmations_track['transcript'],
            intro_media_files=theme['INTRO_MEDIA'],
            intro_text_filename=theme['INTRO_TEXT'],
            affirmation_track_filename=video['file_name'])
        
        complete_video_name, duration = outro_creator.add_outro_video(
            outro_image_filename=theme['OUTRO_IMAGE'],
            outro_text_filename=theme['OUTRO_TEXT'],
            affirmation_track_filename=video['file_name'])

        watermarked_video = watermark_adder.add_watermark(
            image_file_name=theme['WATERMARK'],
            video_file_name=complete_video_name,
            location=theme['WATERMARK_LOCATION'])
    
        video_with_subtitles_name = subtitle_adder.add_subtitles_to_video(
            video_file_name=watermarked_video,
            transcription=video['transcript'],
            output_file_name='sub_' + watermarked_video,
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
        
        
        music_adder.add_music_to_video(
            music_file_name=theme['BACKGROUND_MUSIC'],
            video_name=video_with_subtitles_name,
            output_video_name=affirmation_track['file_name'][:-4] + '.mp4',
            video_length=duration,
            background_music_volume=theme['BACKGROUND_MUSIC_VOLUME'])
        
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                               
def remove_line_of_input_info():
    with open(directories.INPUT_INFO_FILE, 'r') as file:
        lines = file.readlines()

    with open(directories.INPUT_INFO_FILE, 'w') as file:
        file.writelines(lines[1:])  # Skip the first line
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 
main()