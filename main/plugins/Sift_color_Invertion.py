#from algorithms import algorithm
from main.plugins.sift_algorithm import sift_algorithm
#from algorithms.plugin_register import *
from main.algorithms.plugin_register import *

import numpy as np
import cv2



class Sift_color_Invertion(sift_algorithm):
    ### Algorithm name, this name must be the same in the register() function
    name = "Sift+Colorinvertion"
    ## Boolean  that returns whether the registration was successful or not.
    succ = False

    def feature_extraction(self, img1, img2):
        fExt = cv2.xfeatures2d.SIFT_create()
        #gray_negative = abs(255 - img1)
        gray_negative = abs(255 - img2)
        # img_flip_ud = cv2.flip(gray_negative, 1)
        # img_color2 = cv2.flip(img_color2, 1)
        # img2 = img_flip_ud
        img2 = gray_negative
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        img1 = clahe.apply(img1)
        img2 = clahe.apply(img2)
        _, img1 = cv2.threshold(img1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, img2 = cv2.threshold(img2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return fExt, img1, img2




def initialize() -> None:
    register("Sift+Colorinvertion", Sift_color_Invertion)




