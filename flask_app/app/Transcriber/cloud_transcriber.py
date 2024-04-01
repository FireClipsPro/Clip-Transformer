import logging

logging.basicConfig(level=logging.INFO)

class CloudTranscriber:
    def __init__(self, s3=None, output_folder="", input_audio_folder=""):
        self.output_folder = output_folder
        self.input_audio_folder = input_audio_folder
        self.s3 = s3

    def clean_transcription(self, transcription):
        for i in range(len(transcription["word_segments"])):
            transcription["word_segments"][i]['text'] = transcription["word_segments"][i]['word']
            del transcription["word_segments"][i]['word']
            if i == 0:
                if 'start' not in transcription["word_segments"][i]:
                    transcription["word_segments"][i]['start'] = 0
                if 'end' not in transcription["word_segments"][i]:
                    if len(transcription["word_segments"]) > 1:
                        for j in range(1, len(transcription["word_segments"])):
                            if 'start' in transcription["word_segments"][j]:
                                transcription["word_segments"][i]['end'] = transcription["word_segments"][j]['start']
                                break
                    else:
                        transcription["word_segments"][i]['end'] = 0
            else:
                if 'start' not in transcription["word_segments"][i]:
                    transcription["word_segments"][i]['start'] = transcription["word_segments"][i-1]['end']
                if 'end' not in transcription["word_segments"][i]:
                    if len(transcription["word_segments"]) > i+1:
                        for j in range(i+1, len(transcription["word_segments"])):
                            if 'start' in transcription["word_segments"][j]:
                                transcription["word_segments"][i]['end'] = transcription["word_segments"][j]['start']
                                break
                    else:
                        transcription["word_segments"][i]['end'] = transcription["word_segments"][i]['start']
        return transcription
    