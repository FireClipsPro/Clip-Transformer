from youtube_transcript_api import YouTubeTranscriptApi

transcript = YouTubeTranscriptApi.get_transcript('12s9L0VOAMA&ab')

# find the text with longest character length
longest = max(transcript, key=lambda x: x['duration'] * len(x['text']))
print(longest)
print(len(longest['text']))

# find the average character length per text
total = 0
for text in transcript:
    total += len(text['text'])
print(total / len(transcript))

print("size of transcript: ", len(transcript))

# print number of text with more than 160 characters
count = 0
for text in transcript:
    if len(text['text']) > 16:
        count += 1
print(count)