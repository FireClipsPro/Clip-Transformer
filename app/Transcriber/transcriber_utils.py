from pydub import AudioSegment
from pathlib import Path
import os
import json
from google.cloud.speech import RecognizeResponse, LongRunningRecognizeResponse

def convert_to_wav(input_path):
    file_type = input_path.split('.')[-1]
    if file_type == 'wav':
        return input_path
    output_path = get_wav_path(input_path)
    audio = AudioSegment.from_file(input_path, format=file_type)
    audio.export(output_path, format='wav')
    return output_path


def get_wav_path(input_path):
    file_name = input_path.split('/')[-1]
    output_file_name_array = file_name.split('.')
    output_file_name_array[-1] = 'wav'
    output_file_name = '.'.join(output_file_name_array)
    paths_array = input_path.split('/')
    paths_array[-1] = output_file_name
    return '/'.join(paths_array)


def print_transcription(response_standard_wav):
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response_standard_wav.results:
        # The first alternative is the most likely one for this portion.
        alternative = result.alternatives[0]
        # print(f"Transcript: {alternative.transcript}")
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            line = f'"word": "{word}", "start_time": {start_time.seconds}, "end_time": {end_time.seconds}'
            print('{' + line + '},')

def print_transcription_text(stamped_texts):
    for text_obj in stamped_texts:
        print(f'text: {text_obj["text"]}. [start time: {text_obj["start_time"]} and end time: {text_obj["end_time"]}]')

def delete_file(path):
    if Path(path).exists():
        os.remove(path)


def get_blob_id(path):
    file_name_format = path.split('/')[-1]
    return file_name_format.rsplit('.', 1)[0]


def get_absolute_path(current_path, relative_path_to_dst):
    current_path_resolve = Path(current_path).resolve()
    if len(relative_path_to_dst.split('../')) == 1:
        if (len(relative_path_to_dst.split('./')) != 2) or (relative_path_to_dst.split('./')[0] != ''):
            raise Exception('Relative path not specified properly')
        absolute_path = current_path_resolve.parent / relative_path_to_dst
    else:
        num_of_parents = len(relative_path_to_dst.split('../'))
        for i in range(num_of_parents):
            current_path_resolve = current_path_resolve.parent
        absolute_path = current_path_resolve / relative_path_to_dst.split('../')[-1]
    return str(absolute_path.resolve())


def store_transcription(data, path):
    path_obj = Path(path).resolve()
    file_name = path_obj.stem
    if type(data).__name__ == 'RecognizeResponse':
        data = RecognizeResponse.to_json(data)
        file_name = f'{file_name}_short'
    elif type(data).__name__ == 'LongRunningRecognizeResponse':
        data = LongRunningRecognizeResponse.to_json(data)
        file_name = f'{file_name}_long'
    path_obj = path_obj.with_stem(file_name)
    if not os.path.exists(str(path_obj)):
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        path_obj.touch()
    elif os.path.getsize(path) != 0:
        raise Exception('File must be empty!')
    with open(str(path_obj), 'w') as file:
        file.write(json.dumps(data))
    return str(path_obj)


def load_transcription(path):
    path_obj = Path(path).resolve()
    file_name = str(path_obj.stem)
    transcript_length = file_name.rsplit('_', 1)[-1]
    if not os.path.exists(path):
        raise Exception(f'file at path: {path} does not exist!')
    elif os.path.getsize(path) == 0:
        raise Exception('File is empty! No transcript can be loaded from file!')
    with open(path, 'r') as file:
        data = json.loads(file.read())
    if transcript_length.lower() == 'short':
        data = RecognizeResponse.from_json(data)
    elif transcript_length.lower() == 'long':
        data = LongRunningRecognizeResponse.from_json(data)
    return data

