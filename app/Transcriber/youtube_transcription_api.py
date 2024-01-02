from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

class YoutubeTranscriptionApi:
    def __init__(self):
        print("YoutubeTranscriptionApi initialized")

    def extract_video_id(self, url):
        """Extract the video ID from the YouTube URL."""
        # Assuming URL format is like https://www.youtube.com/watch?v=video_id
        if "v=" in url:
            return url.split('v=')[1]
        raise ValueError("Invalid YouTube URL")

    def get_transcription(self, url):
        """Get the transcription of the YouTube video."""
        video_id = self.extract_video_id(url)
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # Get the first (probably the best) transcript
            transcript = transcript_list.find_transcript(['en'])
            english_transcript = transcript.fetch()
            formatted_transcript = self.format(english_transcript)
            return formatted_transcript
        except (TranscriptsDisabled, NoTranscriptFound):
            return "Transcription not available for this video"
    
    def format(self, transcript):
        """Format the transcript to be a list of segments."""
        formatted_transcript = []
        for segment in transcript:
            formatted_segment = {'text': segment['text'],
                                 'start': round(segment['start'], 3),
                                 'end': round(segment['start'] + segment['duration'], 3)}
            formatted_transcript.append(formatted_segment)
            
        return formatted_transcript

# Example usage:
# yt_api = YoutubeTranscriptionApi()
# transcript = yt_api.get_transcription("https://www.youtube.com/watch?v=s1h9EqKFKws")
# print(transcript)
