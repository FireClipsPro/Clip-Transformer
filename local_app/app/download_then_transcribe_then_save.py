from video_downloader import YoutubeVideoDownloader
from Transcriber import CloudTranscriber, AudioExtractor
import configuration.directories as directories
import json
from services import S3
import boto3

# video should be of the form:
# {'link': 'https://www.youtube.com/watch?...'}
# video id gets added later
def download_then_transcribe_then_save(videos):
    # Download the video
    downloader = YoutubeVideoDownloader(output_folder=directories.RAW_VIDEO_FOLDER,
                                        downloaded_videos_folder=directories.DOWNLOADED_VIDEOS_FILE)
    # downloader = YoutubeVideoDownloader(output_folder="./",
    #                                     downloaded_videos_folder=directories.DOWNLOADED_VIDEOS_FILE)
    
    raw_videos = downloader.download_videos(videos)
    
    audio_extractor = AudioExtractor(directories.RAW_VIDEO_FOLDER,
                                     directories.AUDIO_EXTRACTIONS_FOLDER)
    
    audio_extractions = []
    for raw_video in raw_videos:
        audio_extractions.append({})
        audio_extractions[-1]['audio_id'] = raw_video['video_id']
        audio_extractions[-1]['video_name'] = raw_video['video_name']
        audio_extractions[-1]['file_name'] = audio_extractor.extract(raw_video['video_id'])

    transcriber = CloudTranscriber(s3=S3(boto3.client('s3')),
                                   output_folder=directories.TRANSCRIPTS_FOLDER,
                                   input_audio_folder=directories.AUDIO_EXTRACTIONS_FOLDER)
    # video['raw_video_name']
    transcripts = []
    
    for i in range(len(audio_extractions)):
        transcripts.append({})
        transcripts[i]['video_id'] = audio_extractions[i]['file_name']
        transcripts[i]['video_name'] = audio_extractions[i]['video_name']
        transcripts[i]['link'] = raw_videos[i]['link']
        transcript =  transcriber.transcribe(audio_extractions[i]['file_name'])
        transcripts[i]['transcript_word_level'] = transcript['word_segments']
        
    
    transcripts = chunk_transcripts(transcripts)
    # save the transcripts to the output path
    for transcript in transcripts:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Saving transcript to {directories.TRANSCRIPTS_FOLDER}/{transcript['video_id']}.json")
        with open(f"{directories.TRANSCRIPTS_FOLDER}/{transcript['video_id']}.json", "w") as f:
            json.dump(transcript, f)
            
# modify the transcript to only time stamp every 15 seconds
def chunk_transcripts(transcripts):
    for i in range(len(transcripts)):
        chunked_transcript = []
        # chunk the transcript into 30 second chunks
        j = 30
        while True:
            start_chunk = j - 30 if j - 30 > 0 else 0
            end_chunk = j
            # end chunking if the start chunk is past the last word
            if start_chunk > transcripts[i]['transcript_word_level'][-1]['end']:
                # print(f"breaking at start_chunk: {start_chunk}")
                break
            
            index = int(j/30) - 1
            # print(f"building chunked transcript for {start_chunk}-{end_chunk}")
            
            # add the words of the transcript to the chunked transcript
            for word in transcripts[i]['transcript_word_level']:
                if word['start'] <= end_chunk and word['start'] >= start_chunk:
                    # add the word to the chunked transcript
                    # if there is no entry in the transcript for the chunk, add the word
                    print(f"len(chunked_transcript) = {len(chunked_transcript)}, j%30 = {index}")
                    if len(chunked_transcript) < (index + 1):
                        print(f"entry does not exist for chunk {index}, adding word: {word} to {start_chunk}-{end_chunk}")
                        chunked_transcript.append({'text': word['text'],
                                                    'start': start_chunk,
                                                    'end': end_chunk})
                    # if there is an entry in the transcript for the chunk, add the word to the entry
                    else:
                        # print(f"j: {j}, index: {index}")
                        # print(f"word: {word}")
                        # print(f"cunked_transcript: {chunked_transcript}")
                        if chunked_transcript[index]['text']:
                            chunked_transcript[index]['text'] += " " + word['text']
                        # sanity check
                        else:
                            chunked_transcript[index]['text'] = word['text']
                
                if word['start'] > j:
                    # print(f"breaking at word: {word}")
                    break
            # print(f"incrementing j from {j} to {j+30}")
            j += 30
        transcripts[i]['chunked_transcript'] = chunked_transcript

    return transcripts


# links = [{'link': "https://www.youtube.com/watch?v=qJ3uV7coZbA"}]

links = [
        #  {'link': "https://www.youtube.com/watch?v=qJ3uV7coZbA"},
        #  {'link': "https://www.youtube.com/watch?v=AtChcxeaukQ"},
        #  {'link': "https://www.youtube.com/watch?v=q37ARYnRDGc"},
        #  {'link': "https://www.youtube.com/watch?v=tLS6t3FVOTI"},
        #  {'link': "https://www.youtube.com/watch?v=E7W4OQfJWdw"},
        #  {'link': "https://www.youtube.com/watch?v=hFL6qRIJZ_Y"},
        #  {'link': "https://www.youtube.com/watch?v=User8_dkz9s"},
        #  {'link': "https://www.youtube.com/watch?v=OJZ4pjzwDLU"},
        #  {'link': "https://www.youtube.com/watch?v=Z7veiyN4LqU"},
        #  {'link': "https://www.youtube.com/watch?v=OqlPU1CKEpI"}
        ]

download_then_transcribe_then_save(links)