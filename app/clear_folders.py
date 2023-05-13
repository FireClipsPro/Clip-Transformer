from garbage_collection import FileDeleter
import os

file_deleter = FileDeleter()

#print working directory
print("Working directory is: " + os.getcwd())

root = '../media_storage/'

# file_deleter.delete_files_from_folder(f'{root}audio_extractions/')

file_deleter.delete_files_from_folder(f'{root}images/')

file_deleter.delete_files_from_folder(f'{root}videos_made_from_images/')

file_deleter.delete_files_from_folder(f'{root}InputVideos/')

# file_deleter.delete_files_from_folder(f'{root}OutputVideos/')

file_deleter.delete_files_from_folder(f'{root}media_added_videos/')

file_deleter.delete_files_from_folder(f'{root}resized_original_videos/')

print("Files deleted")
