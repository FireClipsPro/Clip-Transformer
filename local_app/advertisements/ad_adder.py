import os
import random
import logging
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips


logging.basicConfig(level=logging.INFO)

class AdAdder:
    def __init__(self,
                 photo_ad_folder,
                 banner_folder,
                 input_video_folder,
                 output_video_folder,
                 image_folder):
        self.photo_ad_folder = photo_ad_folder
        self.banner_folder = banner_folder
        self.input_video_folder = input_video_folder
        self.output_video_folder = output_video_folder
        self.image_folder = image_folder
    
    def add_advertisement_to_photos(self, wants_ads, photos, video_length):
        if not wants_ads:
            logging.info('Ads not wanted')
            return photos

        # get a list of all advertisement photos
        ad_photos = os.listdir(self.photo_ad_folder)

        if not ad_photos:
            logging.info('No ads found')
            return photos

        # calculate the 25% time into the video
        quarter_video_time = video_length * 0.25

        for i, photo in enumerate(photos):
            # if the photo is displayed at 25% into the video, replace it with an ad
            if quarter_video_time >= photo["start_time"] and quarter_video_time <= photo["end_time"]:
                logging.info(f"Replacing photo {photo['image']} with ad at time {quarter_video_time}")
                ad_photo = random.choice(ad_photos)
                logging.info(f"Chose ad {ad_photo}")
                photos[i] = {'image': ad_photo, 'start_time': photo['start_time'], 
                             'end_time': photo['end_time'], 'width': photo['width'], 'height': photo['height']}
                # make sure that the same ad is not used more than once
                ad_photos.remove(ad_photo)
                if not ad_photos:
                    break

            # if this is the last photo, replace it with an ad
            if i == len(photos) - 1 and ad_photos:
                logging.info(f"Replacing photo {photo['image']} with ad at time {photo['start_time']}")
                ad_photo = random.choice(ad_photos)
                photos[i] = {'image': ad_photo, 'start_time': photo['start_time'], 
                             'end_time': photo['end_time'], 'width': photo['width'], 'height': photo['height']}

        return photos
        

    def add_banner(self, want_banner, banner, video, start_times):
        if not want_banner:
            os.replace(self.input_video_folder + video, self.output_video_folder + video)
            return video
        
        # load video
        video_clip = VideoFileClip(self.input_video_folder + video)

        # check if banner is an image or a video
        banner_ext = os.path.splitext(banner)[-1]
        if banner_ext == ".mp4":
            banner_clip = VideoFileClip(self.banner_folder + banner)
        else:
            banner_clip = ImageClip(self.banner_folder + banner).set_duration(video_clip.duration)

        # ensure that banner fits in video dimensions
        video_width, video_height = video_clip.size
        banner_width, banner_height = banner_clip.size

        if banner_width > video_width or banner_height > video_height:
            # scale banner down to fit video dimensions, preserving aspect ratio
            banner_clip = banner_clip.resize(width=video_width)

        clips = []
        last_end_time = 0

        # sort start times
        start_times.sort()

        for start_time in start_times:
             # Skip start_times greater than video's duration
            if start_time >= video_clip.duration:
                continue

            # add banner to video segment starting at start time
            end_time = min(start_time + banner_clip.duration, video_clip.duration)
            banner_segment = video_clip.subclip(start_time, end_time)
            banner_segment = CompositeVideoClip([
                banner_segment,
                banner_clip.set_position(("center", "top")).set_duration(end_time - start_time)
            ])
            clips.append(banner_segment)

            last_end_time = end_time

        # if there is still video remaining after the last end time, add it (without banner)
        if last_end_time < video_clip.duration:
            post_banner_clip = video_clip.subclip(last_end_time, video_clip.duration)
            clips.append(post_banner_clip)

        # concatenate all clips back into final clip
        final_clip = concatenate_videoclips(clips)

        output_video = self.output_video_folder + video
        final_clip.write_videofile(output_video, codec='libx264')
        logging.info(f"Banner added to {video}")
        logging.info(f"Banner saved to {output_video}")
        return output_video