# How to Make a Video

This README will guide you through making a video with the program. First, let's get some background information to understand the repository better.

## 3rd party AI API keys:

Elevenlabs: this is for text to speech.

OpenAI: this is for OpenAI.

The keys should be placed one level up from the actual repository in the files:
elevnlabs_key.txt and OPENAI_API_KEY.txt.
So if your repository is in /code/Clip-Transformer/, then the files should be in the /code/ folder.

# How to run the API tests

1. cd to the root directory of the git
2. run `python -m unittest tests.s3_tests`

# How to test API endpoin

1. cd to run.py and run `python run.py`
2. in browser enter your endpoint for example: http://localhost:5000/background_maker_api/video/
3. enter parameters in the endpoint

# AWS

## How to log into aws:

1. make sure the aws CLI is downloaded and any AWS packages
2. type `aws configure`
3. log in with your access keys

- access keys are stored on aws -> IAM -> users -> find your user account and either generate a new key or use the stored key of your user

## How to list aws buckets:

`aws s3 ls`

## Running Local Version

# Programs

There are three programs in this repository:

- **Affirmation Video Creator**: `/app/make_affirmations.py`
- **Podcast Clip Creator**: `/app/make_pod_clips.py`
- **Text and Audio to Video Creator**: `/app/make_videos.py`

We will be using `make_videos.py` for this guide!

## Media Storage

This folder contains the storage system for creating videos. Each folder inside of media storage corresponds to a program listed above.

- `media_storage/affirmations/` => `app/make_affirmations_video.py`
- `media_storage/pod_clips/` => `app/make_pod_clips.py`
- `media_storage/video_maker/` => `app/make_videos.py`

These folders store videos, images, and `.json` files used during the video creation process. This helps with debugging, as we can identify where a mistake occurred if the final video has errors. It also allows us to track the video's progress.

## Presets

Inside `app/configuration/`, there are 3 preset files. A preset is a configuration of settings, such as fonts, background music, image placement, etc. Each preset corresponds to a setting for a channel and can be thought of as user input that would normally occur inside of a user interface.

## How to Create a Video

### Text to Video

1. Create a `.txt` file containing the script of your video with a title relevant to your video and place the text file inside the folder `media_storage/video_maker/text_input/`. For this example, we will call our input text file `panda.txt`.

2. Open `/media_storage/video_maker/video_maker_input.csv` and inside `video_maker_input.csv`, delete any current entries of `filename,preset` and replace it with `panda.txt,your_preset_name`. For this example, we will use the preset: `curious_primates_long_form`, so the contents of the file would look like this:
   filename,preset
   panda.txt,curious_primates_long_form

3. Now we need three more things to create the video: intro video, a song, background video(s).

4. **For an intro video**: You can either create one yourself or ask Alex to create one. Alex used Canva last time to create an intro for Brain Boost Daily. Once you have your intro file (`.mp4`), add it to the folder `/media_storage/video_maker/intro_videos/`. If you don't have an intro or don't want to use one, set `"WANTS_INTRO"` in `video_maker_presets.py` to `False`.

5. **Adding a song**: Initially, the `/media_storage/video_maker/songs/` folder will be empty because we can't save songs to GitHub due to size limitations. To download a song, find a suitable background song on YouTube, then go into `/app/song_downloader.py` and replace the link in that file with the link to your chosen song. Run `song_downloader.py` to download the song to `media_storage/video_maker/songs/your_song_here.mp3`. Lastly, go to `/app/configuration/video_maker_presets.py` and in your preset, in the `"SONG"` section, enter the file name of your song (without the path), `"SONG": "your_song_name.mp3"`. Now the song is set up.

6. **Adding a background video**: These videos are the visuals that play in the background of your video. The best place to find royalty-free background videos is Pixabay: <https://pixabay.com/>. Add your background video (`.mp4`) to `/media_storage/video_maker/backgrounds/`. Then, go back to `/app/configuration/video_maker_presets.py` and in the `"AUDIO_ONLY_BACKGROUND_MEDIA"` field, enter the name of your video. If you have one video, it should look like `["your_video_name.mp4"]`. If you have multiple videos, list them in the array to make the program cycle through them.

7. **Congratulations, you made it!** You are ready to run `make_videos.py`.
