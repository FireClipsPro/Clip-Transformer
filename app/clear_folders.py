import os
import shutil

class FileDeleter:
    def delete_files_from_folder(self, folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if filename != '.keep':
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

file_deleter = FileDeleter()

# print working directory
print("Working directory is: " + os.getcwd())

root = '../../media_storage/'

file_deleter.delete_files_from_folder(f'{root}audio_extractions/')

file_deleter.delete_files_from_folder(f'{root}images/')

file_deleter.delete_files_from_folder(f'{root}videos_made_from_images/')

file_deleter.delete_files_from_folder(f'{root}InputVideos/')

file_deleter.delete_files_from_folder(f'{root}OutputVideos/')

file_deleter.delete_files_from_folder(f'{root}media_added_videos/')

# file_deleter.delete_files_from_folder(f'{root}resized_original_videos/')

file_deleter.delete_files_from_folder(f'{root}queries/')

file_deleter.delete_files_from_folder(f'{root}video_info/')

print("Files deleted")
