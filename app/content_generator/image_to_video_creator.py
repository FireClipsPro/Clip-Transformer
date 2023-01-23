import subprocess
import os

YOUTUBE_SHORT_ASPECT_RATIO = 9/16
YOUTUBE_SHORT_HALF_HEIGHT = 960
YOUTUBE_SHORT_WIDTH = 1080

class ImageToVideoCreator:
    
    def __init__(self,
                 image_file_path,
                 video_2_image_file_path):
        
        self.image_file_path = image_file_path
        self.video_2_image_file_path = video_2_image_file_path
        print("ImageToVideoCreator created")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# takes in the file name (with extension) of the image and the start and end time of the image in the video
# make the video slowly zooming in on the center of the picture
# if the image is too small, add black bars to the sides
# do not stretch the image
    def convert_images_to_videos(self, images):
        for image in images:
            # initialize the input and output file paths
            input_file = f'{self.image_file_path}{image["image"]}'
            output_file = f'{self.video_2_image_file_path}{image["image"][:-4]}.mp4'
            # delete the output file if it exists
            if os.path.exists(output_file):
                os.remove(output_file)
            
            # if the image size is uneven, change it to even
            if image['width'] % 2 != 0:
                image['width'] -= 1
            if image['height'] % 2 != 0:
                image['height'] -= 1
            
            command = [
                'ffmpeg',
                '-loop', '1',
                '-i', input_file,
                '-vf', f'zoompan=z=\'zoom+0.005\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d=300:s={image["width"]}x{image["height"]}\'',
                '-t', str(image['end_time'] - image['start_time']),
                '-pix_fmt', 'yuv420p',
                output_file
            ]
            subprocess.run(command)
            
            # set the image's video file name
            image['video_file_name'] = f'{image["image"][:-4]}.mp4'
            
            print(f'Created video for {image["image"]}')
            print(f'Dimensions: {image["width"]}x{image["height"]}')
            
        return images

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~           
    def crop_images(self, images, width, height):
        
        for image in images:
            input_file = f'{self.image_file_path}{image["image"]}'
            output_file = f'{self.image_file_path}{image["image"][:-4]}_cropped.jpg'
            
            # if output file does not equal input file, then delete the output file if it exists
            if input_file != output_file:
                if os.path.exists(output_file):
                    os.remove(output_file)
            
            
            # if the image is already the correct size, don't crop it
            if image['width'] == width and image['height'] == height:
                continue
            
            # if the size of the image is within 200 pixels of the desired size crop it
            if abs(image['width'] - width) < 200 and abs(image['height'] - height) < 200:
                print(f'Image {image["image"]} is close to the desired size. Cropping instead.')
                
                # Determine the new width and height of the image
                new_width = image['width']
                new_height = image['height']
                        
                if image['width'] > width:
                    new_width = width
                
                if image['height'] > height:
                    new_height = height
                
                # Create and Run the command to crop the image
                command = [
                    'ffmpeg',
                    '-i', input_file,
                    '-filter:v', f'crop={new_width}:{new_height}',
                    '-c:a', 'copy',
                    output_file
                ]
                subprocess.run(command)
                # replace the old image widths and heights
                image['width'] = new_width
                image['height'] = new_height
                
            else:
                print(f'Image {image["image"]} is too large to crop. Shrinking instead.')
                # Shrink the image to fit in a 1080x960 box, add black bars if ratio is not 9/16
                # Determine the new width and height of the image
                new_width = image['width']
                new_height = image['height']

                if image['width'] > width:
                    new_width = width
                    new_height = int(image['height'] * (width / image['width']))

                if image['height'] > height:
                    new_height = height
                    new_width = int(image['width'] * (height / image['height']))

                # Create and Run the command to shrink the image
                command = [
                    'ffmpeg',
                    '-i', input_file,
                    '-vf', f'scale={new_width}:{new_height}',
                    '-c:a', 'copy',
                    output_file
                ]

                subprocess.run(command)
                
                # replace the old image widths and heights
                image['width'] = new_width
                image['height'] = new_height
                                
            # replace the image file names with the cropped image file names
            image['image'] = f'{image["image"][:-4]}_cropped.jpg'
               
        print("Cropped images")
         
        return images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def find_image_sizes(self, images):
        for image in images:
            
            command = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'csv=s=x:p=0',
                f'{self.image_file_path}{image["image"]}'
            ]
            # if file does not exist, skip it
            if not os.path.exists(f'{self.image_file_path}{image["image"]}'):
                print(f'ERROR: File {self.image_file_path}{image["image"]} does not exist')
                return None
                
            output = subprocess.run(command, stdout=subprocess.PIPE)
            output = output.stdout.decode('utf-8').split('x')
            image['width'] = int(output[0])
            image['height'] = int(output[1])
        
        return images
    
    def process_images(self, images):
        
        images = self.find_image_sizes(images)
        print(images)
        
        if images == None:
            return None
        
        images = self.crop_images(images,
                                  YOUTUBE_SHORT_WIDTH,
                                  YOUTUBE_SHORT_HALF_HEIGHT)
        print(images)

        return self.convert_images_to_videos(images)
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

