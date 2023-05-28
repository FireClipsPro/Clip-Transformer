import logging

logging.basicConfig(level=logging.INFO)

class ImageSpacer:
    def __init__(self):
        print("ImageSpacer created")
    
    def add_spacing_to_images(self, images, time_between_images):
        if time_between_images <= 0:
            logging.info("No spacing needed")
            return images
        
        logging.info(f"Adding {time_between_images} seconds between images")
        for image in images:
            #get the duration of the image
            image_duration = image['end'] - image['start']
            # if time_between_images is greater do nothing and log a warning
            if time_between_images > image_duration:
                logging.warning(f"Time between images is greater than the duration of the image: {image['image']}")
                continue
            # otherwise, add the time_between_images to the start_time of the image
            image['start'] += time_between_images
            
        return images