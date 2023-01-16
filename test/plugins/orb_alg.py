#from main.algorithm import *
from algorithms import algorithm
#from main.plugin_register import *
from algorithms.plugin_register import *
#from main.utils import *

import cv2




class orb_alg():
    name = "Orb"

    def run(self):
        print("works 2")
        #img = cv2.cvtColor(self.fix_image, cv2.COLOR_BGR2GRAY)
        #img2 = cv2.cvtColor(self.mov_image, cv2.COLOR_BGR2GRAY)

        #cv2.imwrite("../test/test_files/gray_test1.jpg", img)
        #cv2.imwrite("../test/test_files/gray_test2.jpg", img2)


def initialize() -> None:
    register("Orb", orb_alg)


