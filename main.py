import cv2
import numpy as np
from imutils import contours


def main ():
    image = cv2.imread('samples/cube12.png')
    image = cv2.resize(image, (615, 820))

    original = image.copy()

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(grayscale, 120, 60)
    #cv2.imshow('Test cube', edges)

    kernel = np.ones((7, 7), np.uint8)
    dilation = cv2.dilate(edges, kernel, iterations = 2)
    #cv2.imshow('Test cube', dilation)

    raw_contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    four_corners = []
    original_img_area = original.shape[0] * original.shape[1]
    max_accepted_area = original_img_area / 3
    four_corners_area_sum = 0
    for cnt in raw_contours:
        epsilon = 0.1 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        area = cv2.contourArea(cnt)

        if 4 == len(approx) and area < max_accepted_area:
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
    cv2.imshow('Test cube', original)

    original_hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)

    mask = np.zeros(original_hsv.shape[:2], np.uint8)
    cv2.drawContours(mask, sorted_contours, 1, (255, 255, 255), -1)
    output = cv2.bitwise_and(original, original, mask = mask)
    
    mean = cv2.mean(output, mask=mask)
    print(mean)

    #cv2.imshow('Test cube', output)
 
    cv2.waitKey(0)
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main ()