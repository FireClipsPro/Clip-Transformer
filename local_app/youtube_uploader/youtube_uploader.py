from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

class YoutubeUploader:
    def __init__(self,
                 upload_file_path):
        self.upload_file_path = upload_file_path

    def upload_video(self, 
                     video_title,
                     video_description,
                     video_tags,
                     video_category,
                     video_language,
                     video_privacy_status,
                     video_playlist):
        # loggin into the channel
        channel = Channel()
        channel.login("./client_secrets.json", "./credentials.storage")

        # setting up the video that is going to be uploaded
        video = LocalVideo(file_path=self.upload_file_path)
        #check if upload_file_path is a valid path
        #if not, raise exception
        if not video.file_path:
            raise Exception("Invalid file path")

        # setting snippet
        video.set_title(video_title)
        video.set_description(video_description)
        video.set_tags(video_tags)
        video.set_category(video_category)
        video.set_default_language(video_language)

        # setting status
        video.set_embeddable(True)
        video.set_license("creativeCommon")
        video.set_privacy_status("public")
        video.set_public_stats_viewable(True)

        # uploading video
        video = channel.upload_video(video)

        
        
#tetsing ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
uploader = YoutubeUploader("../media_storage/OutputVideos/JordanClipResized1.mp4")
uploader.upload_video()