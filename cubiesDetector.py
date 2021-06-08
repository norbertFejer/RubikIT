from cube import ColumnType, Cube, CubeRotation, RowType
from solver import *

from queue import Queue
from threading import Thread
from enum import Enum
import time
import copy

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


    def draw_contours (self, contour_num=-1, color=(0, 255, 0), contour_width=3):
        cv2.drawContours(self._image, self._cubie_contours, -1, (0, 255, 0), 3)


    def attach_image (self, image):
        self._image = image

    def attach_cubie_contours (self, cubie_contours):
        self._cubie_contours = cubie_contours


    def draw_arrow_to_row (self, row_num, arrow_direction, color=(0, 255, 0), thickness=9):
        row_num = row_num.value

        start_point_coord_1 = self._cubie_contours[row_num * 3][1]
        start_point_coord_2 = self._cubie_contours[row_num * 3][3]
        
        arrow_start_coord = (start_point_coord_1 + start_point_coord_2) / 2
        arrow_start_coord = arrow_start_coord.astype(int)
        arrow_start_coord = tuple(arrow_start_coord.flatten())

        end_point_coord_1 = self._cubie_contours[row_num * 3 + 2][0] 
        end_point_coord_2 = self._cubie_contours[row_num * 3 + 2][2]

        arrow_end_coord = (end_point_coord_1 + end_point_coord_2) / 2
        arrow_end_coord = arrow_end_coord.astype(int)
        arrow_end_coord = tuple(arrow_end_coord.flatten())

        for cnt in range(len(self._cubie_contours)):
            rect = cv2.minAreaRect(self._cubie_contours[cnt])
            angle = rect[-1]

        if angle not in range(30, 70):
            if arrow_direction == ArrowDirection.RIGHT:
                cv2.arrowedLine(self._image, arrow_start_coord, arrow_end_coord, color, thickness)
            elif arrow_direction == ArrowDirection.LEFT:
                cv2.arrowedLine(self._image, arrow_end_coord, arrow_start_coord, color, thickness)
            else:
                raise ValueError('Wrong arrow direction!')


    def draw_arrow_to_all_row (self, arrow_direction,  color=(0, 255, 0), thickness=9):
        self.draw_arrow_to_row (RowType.TOP, arrow_direction, color, thickness)
        self.draw_arrow_to_row (RowType.MIDDLE, arrow_direction, color, thickness)
        self.draw_arrow_to_row (RowType.BOTTOM, arrow_direction, color, thickness)


    def draw_arrow_to_column (self, column_num, arrow_direction, color=(0, 255, 0), thickness=9):
        column_num = column_num.value

        start_point_coord_1 = self._cubie_contours[column_num][1] 
        start_point_coord_2 = self._cubie_contours[column_num][3]
        
        arrow_start_coord = (start_point_coord_1 + start_point_coord_2) / 2
        arrow_start_coord = arrow_start_coord.astype(int)
        arrow_start_coord = tuple(arrow_start_coord.flatten())


        end_point_coord_1 = self._cubie_contours[column_num + 6][0] 
        end_point_coord_2 = self._cubie_contours[column_num + 6][2]

        arrow_end_coord = (end_point_coord_1 + end_point_coord_2) / 2
        arrow_end_coord = arrow_end_coord.astype(int)
        arrow_end_coord = tuple(arrow_end_coord.flatten())

        rect = cv2.minAreaRect(self._cubie_contours[0])
        angle = rect[-1]

        if angle not in range(30, 70):
            if arrow_direction == ArrowDirection.DOWN:
                cv2.arrowedLine(self._image, arrow_start_coord, arrow_end_coord, color, thickness)
            elif arrow_direction == ArrowDirection.UP:
                cv2.arrowedLine(self._image, arrow_end_coord, arrow_start_coord, color, thickness)
            else:
                raise ValueError('Wrong arrow direction!')


    def draw_arrow_to_all_column (self, arrow_direction, color=(0, 255, 0), thickness=9):
        self.draw_arrow_to_column (ColumnType.LEFT, arrow_direction, color, thickness)
        self.draw_arrow_to_column (ColumnType.MIDDLE, arrow_direction, color, thickness)
        self.draw_arrow_to_column (ColumnType.RIGHT, arrow_direction, color, thickness)


    def show_image (self, image, image_name=''):
        cv2.imshow(image_name, image)

    
    def draw_rectangle (self, start_point, end_point, color=(255, 0, 0), thickness=9):
        cv2.rectangle(self._image, start_point, end_point, color, thickness)
            

class ColorMapper:
    def __init__(self):
        pass

    def __calculate_color_distance(self, color1, color2):
        dist_r = (color1[0] - color2[0]) * (color1[0] - color2[0])
        dist_g = (color1[1] - color2[1]) * (color1[1] - color2[1])
        dist_b = (color1[2] - color2[2]) * (color1[2] - color2[2])

        return (dist_r + dist_g + dist_b)


    def __get_mapped_color_name(self, color):
        named_colors = {
            "white": (255,255,255),
            "blue": (96, 33, 13),
            "yellow": (29, 137, 189),
            "green": (26, 69, 3),
            "red": (44, 35, 168),
            "orange": (21, 87, 209)
        }

        min_distance = 195075
        closest_color_name = ''
        for color_name, color_value in named_colors.items():
            tmp_dist = self.__calculate_color_distance (color, color_value)

            if tmp_dist < min_distance:
                min_distance = tmp_dist
                closest_color_name = color_name

        return closest_color_name

    def get_contours_color (self, image, contours):
        color_names = []

        for i in range (1, 10):
            mask = np.zeros(image.shape[:2], np.uint8)
            cv2.drawContours(mask, contours, i-1, (255, 255, 255), -1)

            mean_val = cv2.mean(image, mask = mask)
            color_names.append(self.__get_mapped_color_name (mean_val[:3]) )

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
        return self._frame_queue.qsize() > 0


    def stop_stream (self):
        self._stream.release()
        cv2.destroyAllWindows()


class VideoProcessor:
    def __init__ (self, videoStreamer, frame_width, frame_height, state_manager, instruction_helper):
        self._videoStreamer = videoStreamer
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._state_manager = state_manager
        self._imageProcessor = ImageProcessor ()
        self._imageDrawer = ImageDrawer ()
        self._colorMapper = ColorMapper ()
        self._instruction_helper = instruction_helper

        self._instruction_helper.attach_image_drawer (self._imageDrawer)


    def start_processing_video (self):
        self._videoStreamer.start_stream ()

        while True:

            if self._videoStreamer.has_more_frame ():
                self._frame = self._videoStreamer.read_frame ()
                self._frame = cv2.resize(self._frame, (self._frame_width, self._frame_height), fx = 0, fy = 0, interpolation = cv2.INTER_CUBIC)

                self._imageDrawer.attach_image (self._frame)

                frame_for_contours = self._frame.copy()
                frame_for_colors = self._frame.copy()

                self._cubie_contours = self._imageProcessor.get_contours (frame_for_contours)
                if self._cubie_contours:
                    self._imageDrawer.attach_cubie_contours (self._cubie_contours)

                    #self._imageDrawer.draw_contours ()
                    face_colors = self._colorMapper.get_contours_color (frame_for_colors, self._cubie_contours)
                    self._state_manager.persist_state (face_colors)

                    self._instruction_helper.show_next_instruction ()

                self._imageDrawer.draw_rectangle ((170, 100), (470, 500))
                cv2.imshow('RubikIT', self._frame)

            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        self._videoStreamer.stop_stream ()


class Observer:

    def __init__(self):
        self._observers = []
 
    def notify(self, data, modifier = None):
        for observer in self._observers:
            if modifier != observer:
                observer.update(self, data)
 
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
 
    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass


class StateManager (Observer):
    def __init__ (self, safety_level = 10):
        Observer.__init__(self)
        self._safety_level = safety_level
        self._state_change_safety_counter = 0
        self._tmp_actual_state = []
        self._previous_state = []
        self._actual_state = []

    
    def persist_state (self, actual_state):
        if self._previous_state == actual_state:
            self._state_change_safety_counter += 1
        else:
            self._previous_state = actual_state
            self._state_change_safety_counter = 0


        if self._state_change_safety_counter == self._safety_level and self._actual_state != actual_state:
            self._actual_state = actual_state
            self._state_change_safety_counter = 0
            self.notify (actual_state)


    def get_actual_state (self):
        return self._actual_state


class InstructionHelper ():
    def __init__ (self):
        self._imageDrawer = None
        self._actual_instruction = []


    def attach_image_drawer (self, imageDrawer):
        self._imageDrawer = imageDrawer


    def add_instruction (self, instruction):
        self._actual_instruction = instruction
        

    def show_next_instruction (self):
        if self._imageDrawer == None or len(self._actual_instruction) == 0:
            return

        if self._actual_instruction[0] == 'rotate_cube':

            if self._actual_instruction[1] == CubeRotation.RIGTH:
                self._imageDrawer.draw_arrow_to_all_row (ArrowDirection.RIGHT)
                return

            if self._actual_instruction[1] == CubeRotation.LEFT:
                self._imageDrawer.draw_arrow_to_all_row (ArrowDirection.LEFT)
                return

            if self._actual_instruction[1] == CubeRotation.DOWN:
                self._imageDrawer.draw_arrow_to_all_column (ArrowDirection.DOWN)
                return

            if self._actual_instruction[1] == CubeRotation.UP:
                self._imageDrawer.draw_arrow_to_all_column (ArrowDirection.UP)
                return

        if self._actual_instruction[0] == 'rotate_row':
            self._imageDrawer.draw_arrow_to_row (self._actual_instruction[1], self._actual_instruction[2])

        if self._actual_instruction[0] == 'rotate_column':
            self._imageDrawer.draw_arrow_to_column (self._actual_instruction[1], self._actual_instruction[2])

        if self._actual_instruction[0] == 'rotate_front_face':
            print('Front face not implemented yet!')



class SolverProcess:

    def __init__ (self):
        self._stateManager = StateManager ()
        self._instruction_helper = InstructionHelper ()
        self._state_change_counter = 0
        self._last_red_state = []
        self._actual_movement_pos = 0


    def __initialize_state (self):
        stateManager = StateManager ()
        stateManager.attach (self)

        videoStreamer = VideoStreamer(0, 4)
        videoStreamer.start_stream ()

        self._videoProcessor = VideoProcessor (videoStreamer, 640, 640, stateManager, self._instruction_helper)

        video_processor_thread = Thread(target=self._videoProcessor.start_processing_video, args=())
        video_processor_thread.start()


    def solve_cube (self):
        self.__initialize_state ()

        is_invalid_cube = True
        while is_invalid_cube:
            cube_representation = self.__get_cube_representation ()
            cube = Cube(cube_representation)

            try:
                solver = Solver (cube)
                is_invalid_cube = False
            except:
                is_invalid_cube = True

        solver.solve_cube ()

        global movements
        while self._actual_movement_pos < len(movements):
            time.sleep(0.5)
    

    def __get_cube_representation (self):
        self._state_change_counter = 0
        front_face = ''
        top_face = ''
        back_face = ''
        bottom_face = ''
        left_face = ''
        right_face = ''

        sleep_value = 0.5
        while self._state_change_counter != 1:
            time.sleep(sleep_value)
        front_face = self._last_red_state

        instruction = ['rotate_cube', CubeRotation.UP]
        self._instruction_helper.add_instruction (instruction[:])
        while self._state_change_counter != 2:
            time.sleep(sleep_value)
        top_face = self._last_red_state

        while self._state_change_counter != 3:
            time.sleep(sleep_value)
        back_face = self._last_red_state

        while self._state_change_counter != 4:
            time.sleep(sleep_value)
        bottom_face = self._last_red_state

        instruction = ['rotate_cube', CubeRotation.LEFT]
        self._instruction_helper.add_instruction (instruction[:])
        while self._state_change_counter != 5:
            time.sleep(sleep_value)
        left_face = self._last_red_state

        while self._state_change_counter != 6:
            time.sleep(sleep_value)

        while self._state_change_counter != 7:
            time.sleep(sleep_value)
        right_face = self._last_red_state

        instruction = ['rotate_cube', CubeRotation.DOWN]
        self._instruction_helper.add_instruction (instruction[:])
        while self._state_change_counter != 8:
            time.sleep(0.1)

        instruction = ['']
        self._instruction_helper.add_instruction (instruction[:])

        cube_representation = (top_face + 
                                    left_face[6] + left_face[3]+ left_face[0] + front_face[0:3] + right_face[2] + right_face[5] + right_face[8] + back_face[8] + back_face[7] + back_face[6] +
                                    left_face[7] + left_face[4]+ left_face[1] + front_face[3:6] + right_face[1] + right_face[4] + right_face[7] + back_face[5] + back_face[4] + back_face[3] +
                                    left_face[8] + left_face[5]+ left_face[2] + front_face[6:9] + right_face[0] + right_face[3] + right_face[6] + back_face[2] + back_face[1] + back_face[0] +
                                    bottom_face)

        return cube_representation

    
    def __decode_mapped_color (self, color_list):
        face_colors = ''
        for color in color_list:
            face_colors += color[0].upper()

        return face_colors


    def update (self, subject, actual_state):
        print (actual_state)
        self._last_red_state = self.__decode_mapped_color (actual_state)

        if self._state_change_counter >= 8:
            instruction = movements[self._actual_movement_pos]
            self._instruction_helper.add_instruction (instruction[:])

        self._state_change_counter += 1


def test_1 ():
    imageLoader = ImageLoader()
    imageProcessor = ImageProcessor ()
    imageDrawer = ImageDrawer ()

    image = imageLoader.load_image ('C:/MyDocs/University/SoftwareSystemModelling/Rubik_cube_solver/samples', 'real.png')
    image = imageProcessor.resize_image (image, 640, 640)
    original = image.copy ()

    cubie_contours = imageProcessor.get_contours (image)
    print(len(cubie_contours), 'original contour len')
    cubies = imageProcessor.get_valid_cubies_from_contours (cubie_contours)
    print(len(cubies), 'cubies len')

    cm = ColorMapper ()
    face_colors = cm.get_contours_color (original, cubie_contours)
    print (face_colors)

    # p1 = (300, 300)
    # p2 = (0, 360)
    # print('egy intervallumban:', imageProcessor.is_points_in_same_interval(p1, p2))


    imageDrawer.draw_contours (image, cubie_contours)
    imageDrawer.show_image (image)


def main_loop ():
    solverProcess = SolverProcess ()
    solverProcess.solve_cube ()

    



def main ():

    #test_1 ()
    main_loop ()

    cv2.waitKey (0)
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main ()