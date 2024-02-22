import os

def delete_files_with_patterns(directory, patterns):
    for pattern in patterns:
        if pattern == "" or pattern is None:
            print("No patterns provided")
            return
    # Iterate over all the items in the directory
    for item in os.listdir(directory):
        # do not delete anything from the transcripts folder
        if "transcripts" in directory:
            continue
        item_path = os.path.join(directory, item)

        # Check if the item is a directory
        if os.path.isdir(item_path):
            # Recurse into the directory
            delete_files_with_patterns(item_path, patterns)
        else:
            # Check each pattern
            for pattern in patterns:
                if pattern in item:
                    # Delete the file if the pattern is in the filename
                    os.remove(item_path)
                    print(f"Deleted {item_path}")
                    break  # Break the loop once a matching pattern is found

def get_patterns_from_user():
    input_string = input("Enter the patterns separated by #: ")
    return [pattern.strip() for pattern in input_string.split('#')]


# Replace '/path/to/your/directory' with the path to your target directory
root_directory = '/Users/alexander/Documents/Clip_Transformer/media_storage'
patterns = get_patterns_from_user()
delete_files_with_patterns(root_directory, patterns)
