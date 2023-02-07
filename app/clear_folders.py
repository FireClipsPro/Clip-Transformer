from garbage_collection import FileDeleter
import os

file_deleter = FileDeleter()

#print working directory
print("Working directory is: " + os.getcwd())

file_deleter.delete_files_from_folder('./audio_extractions/')

file_deleter.delete_files_from_folder('./images/')

file_deleter.delete_files_from_folder('./videos_made_from_images/')

# file_deleter.delete_files_from_folder('./InputVideos/')

# file_deleter.delete_files_from_folder('./OutputVideos/')

file_deleter.delete_files_from_folder('./media_added_videos/')

file_deleter.delete_files_from_folder('./resized_original_videos/')

file_deleter.delete_files_from_folder('./videos/')

print("Files deleted")
