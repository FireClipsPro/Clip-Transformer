import .directories
import os
import logging

logging.basicConfig(level=logging.INFO)

def create_folder_structure(base_dir):

    for subdirectory in directories.folders_dict.values():
        # remove directories.root from subdirectory
        subdirectory = subdirectory.replace(directories.root, "")
        if os.path.exists(os.path.join(base_dir, subdirectory)):
            logging.info(f"Directory {subdirectory} already exists")
        else:
            logging.info(f"Creating directory {subdirectory}")
            os.makedirs(os.path.join(base_dir, subdirectory), exist_ok=True)

    # create a file called input_info.csv in base_dir
    input_info_path = os.path.join(base_dir, directories.INPUT_INFO_FOLDER)
    if os.path.exists(input_info_path):
        logging.info(f"File {input_info_path} already exists")
    else:
        logging.info(f"Creating file {input_info_path}")
        with open(input_info_path, "w") as f:
            f.write("")
    
create_folder_structure("../../media_storage/")