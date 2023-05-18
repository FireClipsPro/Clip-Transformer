import cv2
import numpy as np
import collections
from moviepy.editor import *
# from video_clipper import VideoClipper
import logging
import time


logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# pip install opencv-python opencv-python-headless moviepy

class HeadTrackingCropper:
    def __init__(self, input_file_path, output_file_path):
        self.INPUT_FILE_PATH = input_file_path
        self.OUTPUT_FILE_PATH = output_file_path
        
    def get_video_size(self, video_file):
        video = cv2.VideoCapture(video_file)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video.release()
        return width, height
    
    def crop_sides_of_video_to_remove_jre_logo(self, input_video):
        video = VideoFileClip(self.INPUT_FILE_PATH + input_video['file_name'])
        video = video.crop(x1=0, y1=0, x2=video.w - 250, y2=video.h)
        output_video = input_video['file_name'][:-4] + "_cropped.mp4"
        video.write_videofile(self.INPUT_FILE_PATH + output_video, threads=4, preset="ultrafast")
        return output_video

 
    # def crop_video_to_face_center(self, input_video, cropped_width, cropped_height):
    #     input_video = self.crop_sides_of_video_to_remove_jre_logo(input_video)
        
    #     # Load the Haar cascade face detector
    #     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    #     output_video = input_video[:-4] + "_centered.mp4"

    #     def detect_face(image):
    #         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #         faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(75, 75))
    #         return faces

    #     # Moving average implementation
    #     moving_average_length = 30
    #     x_positions = collections.deque(maxlen=moving_average_length)
    #     y_positions = collections.deque(maxlen=moving_average_length)

    #     def process_frame(get_frame, t):
    #         frame = get_frame(t) 
    #         faces = detect_face(frame)

    #         if len(faces) > 0:
    #             x, y, w, h = faces[0]
    #             x_positions.append(x + w // 2)
    #             y_positions.append(y + h // 2)
    #         else:
    #             x_positions.append(frame.shape[1] // 2)
    #             y_positions.append(frame.shape[0] // 2)

    #         face_center = (int(sum(x_positions) / len(x_positions)), int(sum(y_positions) / len(y_positions)))

    #         left = face_center[0] - cropped_width // 2
    #         top = face_center[1] - cropped_height // 2
    #         right = left + cropped_width
    #         bottom = top + cropped_height

    #         if left < 0:
    #             right -= left
    #             left = 0
    #         if top < 0:
    #             bottom -= top
    #             top = 0
    #         if right > frame.shape[1]:
    #             left -= right - frame.shape[1]
    #             right = frame.shape[1]
    #         if bottom > frame.shape[0]:
    #             top -= bottom - frame.shape[0]
    #             bottom = frame.shape[0]

    #         cropped_frame = frame[top:bottom, left:right]
    #         return cv2.resize(cropped_frame, (cropped_width, cropped_height))

    #     video_clip = VideoFileClip(self.INPUT_FILE_PATH + input_video)
    #     video_width, video_height = video_clip.size

    #     # Calculate the proportional resizing factors
    #     resize_factor = max(float(cropped_width) / video_width, float(cropped_height) / video_height)
    #     new_video_width = int(video_width * resize_factor)
    #     new_video_height = int(video_height * resize_factor)

    #     # Resize the video to fit the crocpped dimensions
    #     video_clip_resized = video_clip.resize((new_video_width, new_video_height))
    #     cropped_video_clip = video_clip_resized.fl(lambda gf, t: process_frame(gf, t))
    #     cropped_video_clip.duration = video_clip.duration

    #     cropped_video_clip.write_videofile(self.OUTPUT_FILE_PATH + output_video, codec="libx264", audio_codec="aac", threads=4, preset="ultrafast")

    #     return output_video
    
 
    def interpolate_coordinates(self, coordinates, target_fps, source_fps):
        target_frame_count = int(len(coordinates) * target_fps / source_fps)
        interpolated_coordinates = []
        
        for i in range(target_frame_count):
            source_frame = i * source_fps / target_fps
            lower_bound = int(source_frame)
            upper_bound = min(len(coordinates) - 1, lower_bound + 1)
            weight = source_frame - lower_bound
            x = int(round((1 - weight) * coordinates[lower_bound][0] + weight * coordinates[upper_bound][0]))
            y = int(round((1 - weight) * coordinates[lower_bound][1] + weight * coordinates[upper_bound][1]))
            interpolated_coordinates.append((x, y))

        return interpolated_coordinates

    def average_color(self, image, x, y, w, h):
        region = image[y:y+h, x:x+w]
        return np.mean(region, axis=(0, 1))
    
    def euclidean_distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    
    def detect_face(self, image, face_cascade, profile_cascade):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(75, 75))
        profiles = []
        if len(faces) == 0:
            profiles = profile_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7, minSize=(75, 75))
            return profiles
        return faces
    
    def get_largest_face(self, faces):
            if len(faces) == 0:
                return None
            largest_face = faces[0]
            largest_area = faces[0][2] * faces[0][3]
            for face in faces[1:]:
                area = face[2] * face[3]
                if area > largest_area:
                    largest_face = face
                    largest_area = area
            return largest_face
        
    def process_frame(self, 
                      get_frame,
                      t,
                      original_fps,
                      interpolated_face_centers,
                      cropped_width,
                      cropped_height):
        frame = get_frame(t)
        frame_number = int(t * original_fps)
        face_center = interpolated_face_centers[frame_number]
        
        left = face_center[0] - cropped_width // 2
        top = face_center[1] - cropped_height // 2
        right = left + cropped_width
        bottom = top + cropped_height

        if left < 0:
            right -= left
            left = 0
        if top < 0:
            bottom -= top
            top = 0
        if right > frame.shape[1]:
            left -= right - frame.shape[1]
            right = frame.shape[1]
        if bottom > frame.shape[0]:
            top -= bottom - frame.shape[0]
            bottom = frame.shape[0]

        cropped_frame = frame[top:bottom, left:right]
        return cropped_frame
    
    def crop_video_to_face_center(self, input_video, cropped_width, cropped_height):
        #if the video already exists, return it
        output_video = input_video['file_name'][:-4] + "_centered.mp4"
        if os.path.exists(self.OUTPUT_FILE_PATH + output_video):
            input_video['file_name'] = output_video
            return input_video
        
        start_time = time.time()
        print("Beginning crop calculation...")

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

        video_clip = VideoFileClip(self.INPUT_FILE_PATH + input_video['file_name'])
        original_fps = video_clip.fps
        reduced_fps = 5
        video_width, video_height = video_clip.size

        aspect_ratio = float(video_width) / float(video_height)
        new_video_width = int(cropped_height * aspect_ratio)
        new_video_height = cropped_height

        video_clip_resized = video_clip.resize((new_video_width, new_video_height))
        reduced_fps_video_clip = video_clip_resized.set_fps(reduced_fps)

        moving_average_length = 40
        x_positions = collections.deque(maxlen=moving_average_length)
        y_positions = collections.deque(maxlen=moving_average_length)

        face_centers = self.calculate_face_centers(face_cascade, profile_cascade, new_video_width, reduced_fps_video_clip, x_positions, y_positions)

        interpolated_face_centers = self.interpolate_coordinates(face_centers, original_fps, reduced_fps)

        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Time taken to calculate cropping: {time_taken:.2f} seconds")

        cropped_video_clip = video_clip_resized.fl(lambda gf, t: self.process_frame(gf,
                                                                                    t,
                                                                                    original_fps,
                                                                                    interpolated_face_centers,
                                                                                    cropped_width,
                                                                                    cropped_height))
        cropped_video_clip.duration = video_clip.duration

        cropped_video_clip.write_videofile(self.OUTPUT_FILE_PATH + output_video,
                                        codec="libx264",
                                        audio_codec="aac",
                                        threads=4,
                                        preset="ultrafast")
        
        #print the dimensions of the cropped video
        print("Cropped video dimensions: ", cropped_video_clip.size)
        
        input_video['file_name'] = output_video
        return input_video

    def calculate_face_centers(self, face_cascade, profile_cascade, video_width, reduced_fps_video_clip, x_positions, y_positions):
        face_centers = []
        last_face_center = None
        previous_largest_face = None
        previous_frame = None
        corner_color_threshold = 1  # Adjust this value according to your needs
        distance_threshold = int(0.3 * video_width) # Adjust this value according to your needs
        face_color_threshold = 5  # Adjust this value according to your needs
        frame_index = 0

        for frame in reduced_fps_video_clip.iter_frames():
            frame_index += 1
            faces = self.detect_face(frame, face_cascade, profile_cascade)

            if len(faces) > 0:
                largest_face = self.get_largest_face(faces)
                x, y, w, h = largest_face
                face_center = (x + w // 2, y + h // 2)

                # Check if the video has cut to a new face
                if previous_largest_face is not None and previous_frame is not None:
                    distance = self.euclidean_distance(previous_largest_face, face_center)
                    if distance > distance_threshold:
                        color_diff_count, color_diff = self.eval_color_diff_of_frames_corners(previous_frame,
                                                                                              corner_color_threshold,
                                                                                              frame)
                        self.log_color_difference_detection(reduced_fps_video_clip, frame_index, color_diff_count)
                        
                        if color_diff_count >= 2:  # At least 2 out of 4 corners have significant color changes
                            print("Color difference between frames is too large.")
                            print("Color difference is: " + str(color_diff))
                            face_color_diff = self.eval_prev_face_area_color_diff(previous_largest_face, previous_frame, frame)
                            
                            if np.all(face_color_diff > face_color_threshold):
                                self.log_face_switch(distance, face_color_diff)
                                self.reset_moving_averages(x_positions, y_positions)

                x_positions.append(face_center[0])
                y_positions.append(face_center[1])

                face_center = (int(sum(x_positions) / len(x_positions)), int(sum(y_positions) / len(y_positions)))
                last_face_center = face_center
                previous_largest_face = largest_face

            else:
                if last_face_center:
                    face_center = last_face_center
                else:
                    face_center = (frame.shape[1] // 2, frame.shape[0] // 2)

            face_centers.append(face_center)
            previous_frame = frame.copy()
        return face_centers

    def eval_color_diff_of_frames_corners(self, previous_frame, corner_color_threshold, frame):
        corner_w, corner_h = 10, 10  # Adjust the size of the region according to your needs
        frame_width, frame_height = frame.shape[1], frame.shape[0]
        corners = [
                            (0, 0),
                            (frame_width - corner_w, 0),
                            (0, frame_height - corner_h),
                            (frame_width - corner_w, frame_height - corner_h)
                        ]

        color_diff_count = 0
        for x, y in corners:
            current_frame_color = self.average_color(frame, x, y, corner_w, corner_h)
            previous_frame_color = self.average_color(previous_frame, x, y, corner_w, corner_h)
            color_diff = np.abs(current_frame_color - previous_frame_color)

            if np.all(color_diff > corner_color_threshold):
                color_diff_count += 1
        return color_diff_count,color_diff

    def eval_prev_face_area_color_diff(self, previous_largest_face, previous_frame, frame):
        prev_x, prev_y, prev_w, prev_h = previous_largest_face
        current_face_color = self.average_color(frame, prev_x, prev_y, prev_w, prev_h)
        previous_face_color = self.average_color(previous_frame, prev_x, prev_y, prev_w, prev_h)
        face_color_diff = np.abs(current_face_color - previous_face_color)
        return face_color_diff

    def log_face_switch(self, distance, face_color_diff):
        print("Color difference between faces is too large. Cut to new face.")
        print("Face Color difference is: " + str(face_color_diff))
        print("New face distance from old face: " + str(distance))

    def reset_moving_averages(self, x_positions, y_positions):
        x_positions.clear()
        y_positions.clear()

    def log_color_difference_detection(self, reduced_fps_video_clip, frame_index, color_diff_count):
        if color_diff_count >= 1:  # At least 2 out of 4 corners have significant color changes
            print("color_diff_count: " + str(color_diff_count))
            current_frame_time = frame_index / reduced_fps_video_clip.fps
            print(f"Current frame time: {current_frame_time} seconds")

# root = "../"
# RAW_VIDEO_FILE_PATH = f"{root}media_storage/raw_videos/"
# INPUT_FILE_PATH = f"{root}media_storage/InputVideos/"
# RESIZED_FILE_PATH = f"{root}media_storage/resized_original_videos/"

# cropped_width = 1080
# cropped_height = 1920


# cropper = HeadTrackingCropper(INPUT_FILE_PATH, RESIZED_FILE_PATH)

# clipper = VideoClipper(RAW_VIDEO_FILE_PATH, INPUT_FILE_PATH)
# clip = clipper.clip_video("Eliezer.mp4", "1:10", "1:40")
# print("clip is " + str(clip))
# cropped_video_clip = cropper.crop_video_to_face_center(clip['file_name'],
#                                                                     cropped_width,
#                                                                     cropped_height)


