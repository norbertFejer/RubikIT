import cv2
import numpy as np
from imutils import contours


def calculate_color_distance(color1, color2):
    dist_r = (color1[0] - color2[0]) * (color1[0] - color2[0])
    dist_g = (color1[1] - color2[1]) * (color1[1] - color2[1])
    dist_b = (color1[2] - color2[2]) * (color1[2] - color2[2])

    return (dist_r + dist_g + dist_b)


def get_mapped_color_name(color):
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
        tmp_dist = calculate_color_distance (color, color_value)

        if tmp_dist < min_distance:
            min_distance = tmp_dist
            closest_color_name = color_name

    return closest_color_name


class ImageLoader:
    def __init__(self):
        pass

    def load_image (self, path, image_name):
        return cv2.imread(path + '/' + image_name)


class ImageHandler:
    def __init__(self):
        pass

    
    def resize_image (self, image, new_size_x, new_size_y):
        return cv2.resize(image, (new_size_x, new_size_y))

    
    def copy_image (self, image):
        return image.copy ()


    def convert_to_grayscale (self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    def convert_to_hsv (self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    
    def show_image (self, image, image_name=''):
        cv2.imshow(image_name, image)


    def get_edges_from_image (self, image, kernel_size_x, kernel_size_y):
        return cv2.Canny(image, kernel_size_x, kernel_size_y)


    def __create_new_kernel (self, kernel_size_x, kernel_size_y):
        return np.ones((kernel_size_x, kernel_size_y), np.uint8)


    def dilatate_edges (self, edges, iter_num = 3):
        kernel = self.__create_new_kernel (5, 5)
        return cv2.dilate(edges, kernel, iterations = iter_num)

    
    def get_contours_from_image (self, image):
        raw_contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return raw_contours


    def get_four_corners (self, contours, max_accepted_area):
        four_corners = []
        four_corners_area_sum = 0
        for cnt in contours:
            epsilon = 0.1 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if 4 == len(approx):
                area = cv2.contourArea(cnt)

                if area < max_accepted_area:
                    four_corners.append(cnt)
                    four_corners_area_sum += area

        return four_corners, four_corners_area_sum


    def get_cube_pieces (self, four_corners, treshold_area):
        extracted_edges = []
        for cnt in four_corners:
            area = cv2.contourArea(cnt)
            if area > treshold_area:
                extracted_edges.append(cnt)

        return extracted_edges


    def get_sorted_contours (self, unsorted_contours):
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


    def get_approximated_rectangles_from_abstract_contours (self, contours):
        rectangle_shaped_contours = []
        for cnt in contours:
            epsilon = 0.03 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            rectangle_shaped_contours.append(approx)

        return rectangle_shaped_contours


class ImageDrawer:

    def __init__(self):
        pass


    def draw_contours (self, image, contours, contour_num=-1, color=(0, 255, 0), contour_width=3):
        cv2.drawContours(image, contours, contour_num, color, contour_width)


class ColorMapper:
    def __init__(self):
        pass

    def get_contours_color (self, image, contours):
        color_names = []

        for i in range (1, 10):
            mask = np.zeros(image.shape[:2], np.uint8)
            imageDrawer = ImageDrawer ()
            imageDrawer.draw_contours (mask, contours, i-1, (255, 255, 255), -1)

            mean_val = cv2.mean(image, mask = mask)
            color_names.append( get_mapped_color_name (mean_val[:3]) )

        return color_names


def main ():
    imageLoader = ImageLoader ()
    imageHandler = ImageHandler ()

    image = imageLoader.load_image ('./samples', 'cube19.png')
    image = imageHandler.resize_image (image, 615, 820)

    original = imageHandler.copy_image (image)

    original_hsv = imageHandler.convert_to_hsv (original)

    edges = imageHandler.get_edges_from_image (original_hsv, 320, 20)

    dilation = imageHandler.dilatate_edges (edges)

    raw_contours = imageHandler.get_contours_from_image (dilation)

    original_img_area = original.shape[0] * original.shape[1]
    max_accepted_area = original_img_area / 3
    four_corners, four_corners_area_sum =  imageHandler.get_four_corners (raw_contours, max_accepted_area)

    avg_area_of_four_corners = four_corners_area_sum / len(four_corners)
    extracted_edges = imageHandler.get_cube_pieces (four_corners, avg_area_of_four_corners)

    sorted_contours = imageHandler.get_sorted_contours (extracted_edges)
    print(len(sorted_contours))

    sorted_contours_rectangle = imageHandler.get_approximated_rectangles_from_abstract_contours (sorted_contours)

    imageDrawer = ImageDrawer ()
    imageDrawer.draw_contours (original, sorted_contours_rectangle)

    colorMapper = ColorMapper ()
    cubies_colors = colorMapper.get_contours_color (image, sorted_contours)

    print('Cube colors:')
    for i in range (1, 10):
        print(cubies_colors[i-1], end =" ")

        if i % 3 == 0:
            print()
 
    cv2.waitKey(0)
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main ()