import cv2
import numpy as np


img_color = cv2.imread("../media/img/fixed/M32_R2_II_5x.JPG")

img = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

gray_negative = abs(255-img)
img_flip_ud = cv2.flip(gray_negative, 1)

cv2.imwrite("gray_negative.jpg", img_flip_ud)