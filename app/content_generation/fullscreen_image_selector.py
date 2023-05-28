import logging

logging.basicConfig(level=logging.info)

class FullScreenImageSelector:
    def __init__(self, 
                 image_folder_path,
                 image_evaluator):
        self.image_folder_path = image_folder_path
        self.image_evaluator = image_evaluator
    
    def choose_fullscreen_images(self,
                                images,
                                screen_width,
                                screen_height,
                                overlay_zone_width,
                                overlay_zone_height,
                                percent_of_images_to_be_fullscreen):
        # if percent_of_images_to_be_fullscreen <= 0:
        #     logging.info("No fullscreen images requested")
        #     return images
        num_fullscreen_images_required = int(round(len(images) * percent_of_images_to_be_fullscreen))
        logging.info(f"Number of fullscreen images required: {num_fullscreen_images_required}")
        
        images, num_eligible_images = self.determine_eligible_images(images,
                                                                    screen_width,
                                                                    screen_height,
                                                                    num_fullscreen_images_required)
        
        images = self.ensure_spacing_of_fullscreen_images(images,
                                               num_eligible_images=num_eligible_images,
                                               num_fullscreen_images_required=num_fullscreen_images_required,
                                               screen_height=screen_height,
                                               screen_width=screen_width,
                                               overlay_zone_height=overlay_zone_height,
                                               overlay_zone_width=overlay_zone_width)
        
        self.log_image_list(images)
        
        return images
    
    def log_image_list(self, images):
        for image in images:
            logging.info(str(image))

    def ensure_spacing_of_fullscreen_images(self, 
                                images,
                                num_eligible_images,
                                num_fullscreen_images_required,
                                screen_height,
                                screen_width,
                                overlay_zone_height,
                                overlay_zone_width):

        logging.info("Starting select_fullscreen_images")
        logging.info(f"Number of images: {len(images)}")
        logging.info(f"Number of eligible images: {num_eligible_images}")
        logging.info(f"Number of fullscreen images required: {num_fullscreen_images_required}")
        
        num_fullscreen_images_selected = num_eligible_images
        
        eligible_indices = [i for i, image in enumerate(images) if image['eligible']]
        
        logging.info(f"Number of eligible indices: {len(eligible_indices)}")
        
        while num_fullscreen_images_selected > num_fullscreen_images_required and num_fullscreen_images_required != 0:
            min_distance = float('inf')
            index_to_unset = -1
            
            for i in range(len(eligible_indices) - 1):
                if i == 0 and eligible_indices[i] == 0:
                    logging.info(f"index 0 detected, setting it to be unset")
                    index_to_unset = eligible_indices[i]
                    break
                
                distance = abs(eligible_indices[i] - eligible_indices[i + 1])
                
                logging.info(f"Calculating distance for indices {eligible_indices[i]} and {eligible_indices[i + 1]}: {distance}")
                
                if distance < min_distance:
                    min_distance = distance
                    
                    if i == 0 or i + 2 >= len(eligible_indices):
                        index_to_unset = eligible_indices[i + 1]
                        logging.info(f"Setting index_to_unset to {index_to_unset}")
                    else:
                        index_to_unset = (eligible_indices[i] if abs(eligible_indices[i - 1] - eligible_indices[i]) 
                                        < abs(eligible_indices[i + 1] - eligible_indices[i + 2]) 
                                        else eligible_indices[i + 1])
                        logging.info(f"Setting index_to_unset to {index_to_unset}")
            
            if index_to_unset != -1:
                images[index_to_unset]['eligible'] = False
                num_fullscreen_images_selected -= 1
                eligible_indices.remove(index_to_unset)
                logging.info(f"Removed index {index_to_unset} from eligible_indices")
            
            logging.info(f"Number of fullscreen images selected: {num_fullscreen_images_selected}")
            logging.info(f"Updated eligible indices: {eligible_indices}")
        
        images = self.set_image_values(images, screen_height, screen_width, overlay_zone_height, overlay_zone_width)
                
        logging.info("Fullscreen image selection completed")
        return images

    def set_image_values(self, images, screen_height, screen_width, overlay_zone_height, overlay_zone_width):
        
        for image in images:
            if image['eligible']:
                image['fullscreen'] = True
                image['overlay_zone_height'] = screen_height
                image['overlay_zone_width'] = screen_width
                image['overlay_zone_x'] = 0
                image['overlay_zone_y'] = 0
                logging.info("Setting image %s as fullscreen", image)
            else:
                image['fullscreen'] = False
                image['overlay_zone_height'] = overlay_zone_height
                image['overlay_zone_width'] = overlay_zone_width
                image['overlay_zone_x'] = 0
                image['overlay_zone_y'] = int(screen_height / 2)
                logging.info("Setting image %s as non-fullscreen", image)
                
        return images
    
    def determine_eligible_images(self,
                                  images,
                                  screen_width,
                                  screen_height,
                                  num_required_indexes):
        num_eligible_images = 0
        if num_required_indexes <= 0:
            # set all iamge to not be eligible
            for image in images:
                image['eligible'] = False
                
            return images, num_eligible_images
        
        for image in images:
            #if image does not have key height or width, add them
            if 'height' not in image or 'width' not in image:
                logging.info(f"Image {image['image']} does not have height or width, calculating them")
                image['width'], image['height'] = self.image_evaluator.get_image_dimensions(image['image'])
            # h * x = H -> x = H/h -> w * x = new_w -> w * (H/h) = new_w : make sure new_w <= 2 * screen_width
            if (image['height'] >= .6 * screen_height 
                and image['width'] * (screen_height / image['height']) <= 2 * screen_width):
                logging.info(f"Image {image['image']} is eligible")
                image['eligible'] = True
                num_eligible_images += 1
            else:
                image['eligible'] = False
            
        return images, num_eligible_images
    
# Tests ~~~~~