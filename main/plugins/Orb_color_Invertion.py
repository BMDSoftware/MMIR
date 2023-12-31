#from algorithmsPlugin import algorithm
from main.plugins.orb_alg import orb_alg
#from algorithmsPlugin.plugin_register import *
from main.algorithmsPlugin.plugin_register import *

import numpy as np
import cv2


class Orb_color_Invertion(orb_alg):
    ### Algorithm name, this name must be the same in the register() function
    name = "Orb+Colorinvertion"
    ## Boolean  that returns whether the registration was successful or not.
    succ = False

    def feature_extraction(self, img1, img2):
        fExt = cv2.ORB_create(nfeatures=1000)
        #gray_negative = abs(255 - img1)
        gray_negative = abs(255 - img2)
        # img_flip_ud = cv2.flip(gray_negative, 1)
        # img_color2 = cv2.flip(img_color2, 1)
        # img2 = img_flip_ud
        img2 = gray_negative
        #clahe = cv2.createCLAHE()

        #img1 = clahe.apply(img1)
        #img2 = clahe.apply(img2)
        return fExt, img1, img2




def initialize() -> None:
    register("Orb+Colorinvertion", Orb_color_Invertion)
