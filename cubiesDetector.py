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


def main ():
    image = cv2.imread('samples/cube19.png')
    image = cv2.resize(image, (615, 820))

    original = image.copy()

    #grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    original_hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)

    edges = cv2.Canny(original_hsv, 320, 20)
    #cv2.imshow('Test cube', edges)

    kernel = np.ones((5, 5), np.uint8)
    dilation = cv2.dilate(edges, kernel, iterations = 3)
    #cv2.imshow('Test cube', dilation)

    raw_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    four_corners = []
    original_img_area = original.shape[0] * original.shape[1]
    max_accepted_area = original_img_area / 3
    four_corners_area_sum = 0
    for cnt in raw_contours:
        epsilon = 0.1 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if 4 == len(approx):
            area = cv2.contourArea(cnt)

            if area < max_accepted_area:
                four_corners.append(cnt)
                four_corners_area_sum += area

    avg_area_of_four_corners = four_corners_area_sum / len(four_corners)
    extracted_edges = []
    for cnt in four_corners:
        area = cv2.contourArea(cnt)
        if area > avg_area_of_four_corners:
            extracted_edges.append(cnt)

    (cnts, _) = contours.sort_contours(extracted_edges, method="top-to-bottom")
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

    print(len(sorted_contours))

    sorted_contours_rectangle = []
    for cnt in sorted_contours:
        epsilon = 0.03 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        sorted_contours_rectangle.append(approx)

    cv2.drawContours(original, sorted_contours_rectangle, -1, (0, 255, 0), 3)
    #cv2.imshow('Test cube', original)

    print('Cube colors:')
    for i in range (1, 10):
        mask = np.zeros(original_hsv.shape[:2], np.uint8)
        cv2.drawContours(mask, sorted_contours, i-1, (255, 255, 255), -1)

        mean_val = cv2.mean(image, mask = mask)
        #print(mean_val)

        color_name = get_mapped_color_name (mean_val[:3])
        print(color_name, end =" ")

        if i % 3 == 0:
            print()

    cv2.imshow('Test cube', image)
 
    cv2.waitKey(0)
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main ()