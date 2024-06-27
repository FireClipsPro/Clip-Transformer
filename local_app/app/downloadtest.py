from pytube import YouTube

def download_video(url, path):
    print(f"Downloading {url}")
    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if video:
            video.download(output_path=path)
            print(f"Downloaded '{yt.title}' successfully.")
        else:
            print("No suitable video found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=ZgMw__KdjiI"
    download_path = "./"
    download_video(video_url, download_path)
