from cube import ColumnType, Cube, CubeRotation, RowType
from solver import Solver

from queue import Queue
from threading import Thread
from enum import Enum
import time

import numpy as np
from numpy.lib.function_base import angle
from numpy.lib.type_check import imag

import cv2
from imutils import contours

import sys


class ArrowDirection(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


class ImageLoader:
    def __init__(self):
        pass

    def load_image (self, path, image_name):
        return cv2.imread(path + '/' + image_name)


class ImageProcessor:
    def __init__(self):
        pass

    
    def resize_image (self, image, new_size_x, new_size_y):
        return cv2.resize(image, (new_size_x, new_size_y))

    
    def copy_image (self, image):
        return image.copy ()


    def __convert_to_grayscale (self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    def __convert_to_hsv (self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


    def __get_edges_from_image (self, image, kernel_size_x, kernel_size_y):
        return cv2.Canny(image, kernel_size_x, kernel_size_y)


    def __create_new_kernel (self, kernel_size_x, kernel_size_y):
        return np.ones((kernel_size_x, kernel_size_y), np.uint8)


    def __dilatate_edges (self, edges, iter_num = 3):
        kernel = self.__create_new_kernel (3, 3)
        return cv2.dilate(edges, kernel, iterations = iter_num)

    
    def __get_contours_from_image (self, image):
        raw_contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return raw_contours


    def __get_four_corners (self, contours, max_accepted_area, min_accepted_area):
        four_corners = []
        for cnt in contours:
            epsilon = 0.08 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if 4 == len(approx):

                (x, y, w, h) = cv2.boundingRect(approx)
                #aspect_ratio = w / float(h)

                # aspect_ratio >= 0.8 and aspect_ratio <= 1.2
                if (w*h < max_accepted_area) and (w*h > min_accepted_area):
                    four_corners.append(cnt)

        return four_corners


    def __get_cube_pieces (self, four_corners, treshold_area):
        extracted_edges = []
        for cnt in four_corners:
            area = cv2.contourArea(cnt)
            if area > treshold_area:
                extracted_edges.append(cnt)

        return extracted_edges


    def __get_sorted_contours (self, unsorted_contours):
        (cnts, _) = contours.sort_contours(unsorted_contours, method="top-to-bottom")
        # Take each row of 3 and sort from left-to-right
        cube_rows = []
        row = []
        for (i, c) in enumerate(cnts, 1):
            row.append(c)
            if i % 3 == 0:  
                (cnts, _) = contours.sort_contours(row, method="left-to-right")
                cube_rows.append(cnts)
                row = []

        sorted_contours = []
        for row in cube_rows:
            for cnt in row:
                sorted_contours.append(cnt)

        return sorted_contours


    def __get_approximated_rectangles_from_abstract_contours (self, contours):
        rectangle_shaped_contours = []
        for cnt in contours:
            epsilon = 0.03 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            rectangle_shaped_contours.append(approx)

        return rectangle_shaped_contours


    def get_contours (self, image):
        #original_hsv = self.__convert_to_hsv (image)
        mask = cv2.imread('C:/MyDocs/University/SoftwareSystemModelling/Rubik_cube_solver/samples/mask.png')
        image = cv2.bitwise_and(image, mask)

        grayscale = self.__convert_to_grayscale (image)

        grayscale = cv2.GaussianBlur(grayscale,(9,3),3)

        laplacian = cv2.Laplacian(grayscale, cv2.CV_16S, ksize=5)
        laplacian = cv2.convertScaleAbs(laplacian)

        edges = self.__get_edges_from_image (laplacian, 120, 240)
        dilation = self.__dilatate_edges (edges, 3)

        #cv2.imshow('RubikIT', dilation)
        #cv2.waitKey (0)

        #laplacian = laplacian.astype(np.uint8)
        #laplacian=(laplacian-laplacian.min())/(laplacian.max()-laplacian.min())


        #canny1 = cv2.Canny(np.uint8(laplacian* 255), 320, 20)

        raw_contours = self.__get_contours_from_image (dilation)
        #print(len(raw_contours))

        max_accepted_area = int(image.shape[0] / 3) * int(image.shape[0] / 3)
        min_accepted_area = int(image.shape[0] / 16) * int(image.shape[0] / 16)

        four_corners = self.__get_four_corners (raw_contours, max_accepted_area, min_accepted_area)
        #print(len(four_corners), 'four_corners...')

        detected_cubies_contour = self.get_valid_cubies_from_contours (four_corners)
        if len(detected_cubies_contour) == 0:
             return []

        detected_cubies_contour = self.__get_sorted_contours (detected_cubies_contour)

        if len(detected_cubies_contour) == 9:
            return detected_cubies_contour
        
        return []

    
    def get_contour_max_boundary_coordinates (self, contour):
        max_x, max_y, min_x, min_y = 0, 0, sys.maxsize, sys.maxsize
        for cnt in contour:
            actual_point_x = cnt[0][0]
            actual_point_y = cnt[0][1]
            
            if actual_point_x > max_x:
                max_x = actual_point_x
            elif actual_point_x < min_x:
                min_x = actual_point_x

            if actual_point_y > max_y:
                max_y = actual_point_y
            elif actual_point_y < min_y:
                min_y = actual_point_y

        return (min_x, min_y), (max_x, max_y)


    def is_points_in_same_interval (self, point1, point2, tolerance=30):

        if (((point2[0] < point1[0] + tolerance) and 
                (point2[0] > point1[0] - tolerance)) or
                ((point2[1] < point1[1] + tolerance) and
                (point2[1] > point1[1] - tolerance))):
            return True
        return False


    def get_valid_cubies_from_contours (self, contours):

        cubie_contours = []
        for actual_cnt in contours:
            start_coord_actual_cnt, end_coord_actual_cnt = self.get_contour_max_boundary_coordinates (actual_cnt)

            match_x_coord_count = 0
            match_y_coord_count = 0
            for cnt in contours:
                start_coord_other_cnt, end_coord_other_cnt = self.get_contour_max_boundary_coordinates (cnt)

                # checking if we selected the same contour as the actual one
                if ((start_coord_actual_cnt[0] == start_coord_other_cnt[0]) and
                        (start_coord_actual_cnt[1] == start_coord_other_cnt[1]) and
                        (end_coord_actual_cnt[0] == end_coord_other_cnt[0]) and
                        (end_coord_actual_cnt[1] == end_coord_other_cnt[1])):
                    continue

                if self.is_points_in_same_interval (start_coord_actual_cnt, start_coord_other_cnt):
                    match_x_coord_count += 1
                
                if self.is_points_in_same_interval (end_coord_actual_cnt, end_coord_other_cnt):
                    match_y_coord_count += 1

            if match_x_coord_count >= 4 and match_y_coord_count >= 4:
                cubie_contours.append (actual_cnt)

        return cubie_contours


    def __is_all_countour_a_cubie (self, contours):
        
        tolerance = 30
        start_coord_1, end_coord_1 = self.get_contour_max_boundary_coordinates (contours[0])
        start_coord_2, end_coord_2 = self.get_contour_max_boundary_coordinates (contours[4])
        if not self.is_points_in_same_interval (end_coord_1, start_coord_2, tolerance):
            return False

        start_coord_1, end_coord_1 = self.get_contour_max_boundary_coordinates (contours[4])
        start_coord_2, end_coord_2 = self.get_contour_max_boundary_coordinates (contours[8])
        if not self.is_points_in_same_interval (end_coord_1, start_coord_2, tolerance):
            return False

        start_coord_1, end_coord_1 = self.get_contour_max_boundary_coordinates (contours[3])
        start_coord_2, end_coord_2 = self.get_contour_max_boundary_coordinates (contours[7])
        if not self.is_points_in_same_interval (end_coord_1, start_coord_2, tolerance):
            return False

        start_coord_1, end_coord_1 = self.get_contour_max_boundary_coordinates (contours[1])
        start_coord_2, end_coord_2 = self.get_contour_max_boundary_coordinates (contours[5])
        if not self.is_points_in_same_interval (end_coord_1, start_coord_2, tolerance):
            return False

        return True

        


class ImageDrawer:

    def __init__(self):
        pass


    def draw_contours (self, image, contours, contour_num=-1, color=(0, 255, 0), contour_width=3):
        cv2.drawContours(image, contours, -1, (0, 255, 0), 3)


    def draw_arrow_to_row (self, image, cubie_contours, row_num, arrow_direction, color=(0, 255, 0), thickness=9):
        row_num = row_num.value

        start_point_coord_1 = cubie_contours[row_num * 3][1]
        start_point_coord_2 = cubie_contours[row_num * 3][3]
        
        arrow_start_coord = (start_point_coord_1 + start_point_coord_2) / 2
        arrow_start_coord = arrow_start_coord.astype(int)
        arrow_start_coord = tuple(arrow_start_coord.flatten())

        end_point_coord_1 = cubie_contours[row_num * 3 + 2][0] 
        end_point_coord_2 = cubie_contours[row_num * 3 + 2][2]

        arrow_end_coord = (end_point_coord_1 + end_point_coord_2) / 2
        arrow_end_coord = arrow_end_coord.astype(int)
        arrow_end_coord = tuple(arrow_end_coord.flatten())

        for cnt in range(len(cubie_contours)):
            rect = cv2.minAreaRect(cubie_contours[cnt])
            angle = rect[-1]

        if angle not in range(30, 70):
            if arrow_direction == ArrowDirection.RIGHT:
                cv2.arrowedLine(image, arrow_start_coord, arrow_end_coord, color, thickness)
            elif arrow_direction == ArrowDirection.LEFT:
                cv2.arrowedLine(image, arrow_end_coord, arrow_start_coord, color, thickness)
            else:
                raise ValueError('Wrong arrow direction!')


    def draw_arrow_to_all_row (self, image, cubie_contours, arrow_direction,  color=(0, 255, 0), thickness=9):
        self.draw_arrow_to_row (image, cubie_contours, RowType.TOP, arrow_direction, color)
        self.draw_arrow_to_row (image, cubie_contours, RowType.MIDDLE, arrow_direction, color)
        self.draw_arrow_to_row (image, cubie_contours, RowType.BOTTOM, arrow_direction, color)


    def draw_arrow_to_column (self, image, cubie_contours, column_num, arrow_direction, color=(0, 255, 0), thickness=9):
        column_num = column_num.value

        start_point_coord_1 = cubie_contours[column_num][1] 
        start_point_coord_2 = cubie_contours[column_num][3]
        
        arrow_start_coord = (start_point_coord_1 + start_point_coord_2) / 2
        arrow_start_coord = arrow_start_coord.astype(int)
        arrow_start_coord = list(arrow_start_coord.flatten())


        end_point_coord_1 = cubie_contours[column_num + 6][0] 
        end_point_coord_2 = cubie_contours[column_num + 6][2]

        arrow_end_coord = (end_point_coord_1 + end_point_coord_2) / 2
        arrow_end_coord = arrow_end_coord.astype(int)
        arrow_end_coord = list(arrow_end_coord.flatten())

        rect = cv2.minAreaRect(cubie_contours[0])
        angle = rect[-1]

        if angle not in range(30, 70):
            if arrow_direction == ArrowDirection.DOWN:
                cv2.arrowedLine(image, arrow_start_coord, arrow_end_coord, color, thickness)
            elif arrow_direction == ArrowDirection.UP:
                cv2.arrowedLine(image, arrow_end_coord, arrow_start_coord, color, thickness)
            else:
                raise ValueError('Wrong arrow direction!')


    def draw_arrow_to_all_column (self, image, cubie_contours, arrow_direction, color=(0, 255, 0), thickness=9):
        self.draw_arrow_to_column (image, cubie_contours, ColumnType.LEFT, arrow_direction, color, thickness)
        self.draw_arrow_to_column (image, cubie_contours, ColumnType.MIDDLE, arrow_direction, color, thickness)
        self.draw_arrow_to_column (image, cubie_contours, ColumnType.RIGHT, arrow_direction, color, thickness)


    def show_image (self, image, image_name=''):
        cv2.imshow(image_name, image)

    
    def draw_rectangle (self, image, start_point, end_point, color=(255, 0, 0), thickness=9):
        cv2.rectangle(image, start_point, end_point, color, thickness)
            

class ColorMapper:
    def __init__(self):
        pass

    def calculate_color_distance(self, color1, color2):
        dist_r = (color1[0] - color2[0]) * (color1[0] - color2[0])
        dist_g = (color1[1] - color2[1]) * (color1[1] - color2[1])
        dist_b = (color1[2] - color2[2]) * (color1[2] - color2[2])

        return (dist_r + dist_g + dist_b)


    def get_mapped_color_name(self, color):
        named_colors = {
            "white": (255,255,255),
            "blue": (255, 0, 0),
            "yellow": (45, 175, 220),
            "green": (0, 255, 0),
            "red": (0, 0, 255),
            "orange": (0, 85, 255)
        }

        min_distance = 195075
        closest_color_name = ''
        for color_name, color_value in named_colors.items():
            tmp_dist = self.calculate_color_distance (color, color_value)

            if tmp_dist < min_distance:
                min_distance = tmp_dist
                closest_color_name = color_name

        return closest_color_name

    def get_contours_color (self, image, contours):
        color_names = []

        for i in range (1, 10):
            mask = np.zeros(image.shape[:2], np.uint8)
            imageDrawer = ImageDrawer ()
            imageDrawer.draw_contours (mask, contours, i-1, (255, 255, 255), -1)

            mean_val = cv2.mean(image, mask = mask)
            color_names.append(self.get_mapped_color_name (mean_val[:3]) )

        return color_names


class VideoStreamer:

    def __init__(self, camera_num, queueSize=4):
        self._stream = cv2.VideoCapture(camera_num)
        self._frame_queue = Queue(maxsize=queueSize)


    def start_stream(self):
        streamer_thread = Thread(target=self.__read_frames_to_queue, args=())
        streamer_thread.daemon = True
        streamer_thread.start()
        return self

    
    def __read_frames_to_queue(self):
        while self._stream.isOpened():

            if not self._frame_queue.full():
                (grabbed, frame) = self._stream.read ()

                if not grabbed:
                    continue

                self._frame_queue.put(frame)


    def read_frame(self):
        if self._frame_queue.qsize() > 0:
            return self._frame_queue.get()
        return []


    def has_more_frame (self):
        print(self._frame_queue.qsize())
        return self._frame_queue.qsize() > 0


    def stop_stream (self):
        self._stream.release()
        cv2.destroyAllWindows()


class VideoProcessor:
    def __init__ (self, videoStreamer, frame_width, frame_height):
        self._videoStreamer = videoStreamer
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._imageProcessor = ImageProcessor ()
        self._imageDrawer = ImageDrawer ()


    def start_processing_video (self):
        print ('VideoProcessor is started...')

        self._videoStreamer.start_stream ()

        while True:

            if self._videoStreamer.has_more_frame ():
                frame = self._videoStreamer.read_frame ()
                frame = cv2.resize(frame, (self._frame_width, self._frame_height), fx = 0, fy = 0, interpolation = cv2.INTER_CUBIC)

                cubie_contours = self._imageProcessor.get_contours (frame)
                self._imageDrawer.draw_contours (frame, cubie_contours)
                self._imageDrawer.draw_rectangle (frame, (170, 100), (470, 500))
                cv2.imshow('RubikIT', frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        self._videoStreamer.stop_stream ()



def test_1 ():
    imageLoader = ImageLoader()
    imageProcessor = ImageProcessor ()
    imageDrawer = ImageDrawer ()

    image = imageLoader.load_image ('C:/MyDocs/University/SoftwareSystemModelling/Rubik_cube_solver/samples', 'real.png')
    image = imageProcessor.resize_image (image, 640, 640)

    cubie_contours = imageProcessor.get_contours (image)
    print(len(cubie_contours), 'original contour len')
    cubies = imageProcessor.get_valid_cubies_from_contours (cubie_contours)
    print(len(cubies), 'cubies len')

    # p1 = (300, 300)
    # p2 = (0, 360)
    # print('egy intervallumban:', imageProcessor.is_points_in_same_interval(p1, p2))


    imageDrawer.draw_contours (image, cubie_contours)
    imageDrawer.show_image (image)


def main_loop ():
    videoStreamer = VideoStreamer(0, 4)
    videoStreamer.start_stream ()

    videoProcessor = VideoProcessor (videoStreamer, 640, 640)
    videoProcessor.start_processing_video ()



def main ():

    #test_1 ()
    main_loop ()

    cv2.waitKey (0)
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main ()