from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
import json
import logging

logging.basicConfig(level=logging.INFO)

class PauseRemover:
    def __init__(self, input_video_folder, output_video_folder):
        self.input_video_folder = input_video_folder
        self.output_video_folder = output_video_folder

    def remove_pauses(self, clipped_video, transcript, maximum_pause_length):
        new_video = self.remove_video_pauses(clipped_video['file_name'], transcript, maximum_pause_length)

        # Write the new video
        clipped_video['file_name'] = clipped_video['file_name'].split('.')[0] + '_no_pauses.mp4'
        new_video.write_videofile(self.output_video_folder + clipped_video['file_name'])
        
        new_transcript = self.remove_transcript_pauses(transcript,maximum_pause_length)

        clipped_video['end_time_sec'] = new_video.duration
        
        return clipped_video, new_transcript

    def remove_video_pauses(self,
                            file_name,
                            transcript,
                            maximum_pause_length):
        video = VideoFileClip(self.input_video_folder + file_name)

        new_video_clips = []
        last_gap_end = 0
        for i in range(len(transcript)):
            word = transcript[i]

            if i != len(transcript) - 1:
                next_word = transcript[i + 1]
                pause_length = next_word['start'] - word['end']

                if pause_length > maximum_pause_length:
                    logging.info(" ______ LONG PAUSE DETECTED ______")
                    logging.info("at time " + str(word['end']) + " found a pause of length " + str(pause_length) + " seconds")

                    logging.info("word is \"" + word['text'] + "\" and next word is \"" + next_word['text'] + "\"")
                    
                    end_of_dialogue = word['end'] + (maximum_pause_length / 2)
                    logging.info("the entire pause is from " + str(word['end']) + " to " + str(next_word['start']))
                    logging.info(" removing pause from " + str(end_of_dialogue) + " to " + str(next_word['start']))
                    new_clip = video.subclip(last_gap_end, end_of_dialogue)
                    logging.info("new clip is from " + str(last_gap_end) + " to " + str(end_of_dialogue))
                    last_gap_end = next_word['start'] - (maximum_pause_length / 2)

                    new_video_clips.append(new_clip)
            else:
                new_video_clips.append(video.subclip(last_gap_end, word['end']))

        # Concatenate the new video clips
        new_video = concatenate_videoclips(new_video_clips)
        return new_video

    # TODO: re-jig this so that it works with the new transcript format
    def remove_transcript_pauses(self, transcript, maximum_pause_length):
        time_substracted_from_video = 0
        new_transcript = []
        for i in range(len(transcript)-1):  # subtract 1 to prevent IndexError
            word = transcript[i]
            
            new_transcript.append({'text': word['text'],
                                   'start': word['start'] - time_substracted_from_video,
                                   'end': word['end'] - time_substracted_from_video})
            
            next_word = transcript[i + 1]
            pause_length = next_word['start'] - word['end']

            if pause_length > maximum_pause_length:
                time_substracted_from_video += pause_length - maximum_pause_length
        
        # We still need to process the last word
        word = transcript[-1]
        new_transcript.append({'text': word['text'],
                               'start': word['start'] - time_substracted_from_video,
                               'end': word['end'] - time_substracted_from_video})
        return new_transcript

# How to use the PauseRemover class  
# root = "../../media_storage/"
# RESIZED_FOLDER = f"{root}resized_original_videos/"
# AUDIO_EXTRACTIONS_FOLDER = f"{root}audio_extractions/"

# INPUT_FOLDER = f"{root}InputVideos/"

# remover = PauseRemover(RESIZED_FOLDER, RESIZED_FOLDER)
# # get transcript from json file
# with open(AUDIO_EXTRACTIONS_FOLDER + "Eliezer_(0, 0)_(0, 25)_centered.mp3.json", "r") as f:
#     transcript = json.load(f)

# remover.remove_pauses("Eliezer_(0, 0)_(0, 25)_centered.mp4",
#                             transcript['word_segments'],
#                             0.4)