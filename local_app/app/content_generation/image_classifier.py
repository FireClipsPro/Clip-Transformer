from transformers import pipeline
from PIL import Image
import time

class ImageClassifier:
    
    def __init__(self, image_folder_path, checkpoint="openai/clip-vit-base-patch32"):
        self.image_folder_path = image_folder_path
        self.detector = pipeline(model=checkpoint, task="zero-shot-image-classification")

    def classify(self, image_file_name, description):
        start_time = time.time()
        image = self.get_image_from_path(image_file_name)
        labels = description.split()
        predictions = self.detector(image, candidate_labels=labels)
        end_time = time.time()
        
        print(f"Classification took {end_time - start_time} seconds.")
        
        # print predictions
        for prediction in predictions:
            print(f"{prediction['label']}: {prediction['score']}")
            
        # return a rating out of 10 based on the highest scoring labellll
        best_label = max(predictions, key=lambda x: x['score'])
        rating = best_label['score'] * 10
        return rating

    def get_image_from_path(self, image_file_name):
        return Image.open(self.image_folder_path + image_file_name)

# testing ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# classifier = ImageClassifier(image_folder_path="../../media_storage/images/")
# image_file_name = "jungle_navigation_2.jpg"
# description = "jungle navigation"
# rating, best_match_label = classifier.classify(image_file_name, description)
# print(f"Rating: {rating}/10")
# print(f"Best matching label: {best_match_label}")

# image_file_name = "jungle_navigation_0.jpg"
# description = "jungle navigation"
# rating, best_match_label = classifier.classify(image_file_name, description)
# print(f"Rating: {rating}/10")
# print(f"Best matching label: {best_match_label}")

# image_file_name = "desert_city_0.jpg"
# description = "Desert City"
# rating, best_match_label = classifier.classify(image_file_name, description)
# print(f"Rating: {rating}/10")
# print(f"Best matching label: {best_match_label}")

# image_file_name = "desert_castle_0.jpg"
# description = "desert castle"
# rating, best_match_label = classifier.classify(image_file_name, description)
# print(f"Rating: {rating}/10")
# print(f"Best matching label: {best_match_label}")