

class FileDeleter:
    
    def __init__(self):
        print("FileDeleter created")
    
    def delete_files_from_folder(self, folder_path):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(e)
                
    def delete_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("The file does not exist")
        
        
        
        
        
        
        
        