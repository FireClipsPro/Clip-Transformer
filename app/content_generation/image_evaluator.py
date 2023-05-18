import time
import cv2
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='app.log'),
        logging.StreamHandler()
    ]
)

MIN_COLOR_COUNT = 60000

class ImageEvaluator:
    def __init__(self, image_file_path):
        self.IMAGE_FILE_PATH = image_file_path
    
    def evaluate_colorfulness(self, image_file_name):
        logging.info(f"Starting evaluate_colorfulness method for image: {image_file_name}")
        start_time = time.time()

        # Load image
        img = cv2.imread(self.IMAGE_FILE_PATH + image_file_name)
        if img is None:
            logging.error(f"Could not load image: {image_file_name}")
            return

        # Convert image to RGB (OpenCV uses BGR by default)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Split image into its RGB components
        (R, G, B) = cv2.split(img.astype("float"))

        # Compute rg = R - G
        rg = np.absolute(R - G)

        # Compute yb = 0.5 * (R + G) - B
        yb = np.absolute(0.5 * (R + G) - B)

        # Compute the mean and standard deviation of both `rg` and `yb`
        (rbMean, rbStd) = (np.mean(rg), np.std(rg))
        (ybMean, ybStd) = (np.mean(yb), np.std(yb))

        # Combine the mean and standard deviations
        stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
        meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))

        # Derive the "colorfulness" metric and log it
        colorfulness = stdRoot + (0.3 * meanRoot)
        logging.info(f"Colorfulness: {colorfulness}")
        logging.info(f"Time taken to evaluate colorfulness: {time.time() - start_time}")

        return colorfulness
    
    def is_colorful_enough(self, image_file_name):
        logging.info(f"Starting estimate_color_count method for image: {image_file_name}")
        start_time = time.time()

        # Load image
        img = cv2.imread(self.IMAGE_FILE_PATH + image_file_name)
        if img is None:
            logging.error(f"Could not load image: {image_file_name}")
            return

        # Flatten image data
        flat_img_data = img.reshape(-1, img.shape[-1])

        # Find unique colors
        unique_colors = np.unique(flat_img_data, axis=0)
        color_count = unique_colors.shape[0]
        
        logging.info(f"Estimated number of colors: {color_count}")
        logging.info(f"Time taken to estimate color count: {time.time() - start_time}")
        
        return color_count > MIN_COLOR_COUNT
    
# Test ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# image_evaluator = ImageEvaluator("../../media_storage/images/")

# image_list = [
#     "success_through_challenges_0.jpg",
#     "incremental_progress_weightlifting_0.jpg",
#     "weightlifting_progression_0.jpg",
#     "small_weightlifting_increments_progress_0.jpg"
# ]

# for image in image_list:
#     logging.info(image)
#     logging.info(image_evaluator.estimate_color_count(image))
