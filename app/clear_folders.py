from garbage_collection import FileDeleter
import os

file_deleter = FileDeleter()

#print working directory
print("Working directory is: " + os.getcwd())

# file_deleter.delete_files_from_folder('./media_storage/audio_extractions/')

file_deleter.delete_files_from_folder('./media_storage/images/')

file_deleter.delete_files_from_folder('./media_storage/videos_made_from_images/')

# file_deleter.delete_files_from_folder('./media_storage/InputVideos/')

# file_deleter.delete_files_from_folder('./media_storage/OutputVideos/')

file_deleter.delete_files_from_folder('./media_storage/media_added_videos/')

file_deleter.delete_files_from_folder('./media_storage/resized_original_videos/')

file_deleter.delete_files_from_folder('./media_storage/videos/')

print("Files deleted")
