#from main.algorithm import *
from algorithms import algorithm
#from main.plugin_register import *
from algorithms.plugin_register import *
#from main.utils import *

import cv2



class sift_algorithm(algorithmCore):
    name = "Sift"

    def run(self):
        print("works")
        print("fix" , self)
        print("fix" , self.fix_image)
        #img = cv2.cvtColor(self.fix_image, cv2.COLOR_BGR2GRAY)
        #img2 = cv2.cvtColor(self.mov_image, cv2.COLOR_BGR2GRAY)

        #cv2.imwrite("../test/test_files/gray_test1.jpg", img)
        #cv2.imwrite("../test/test_files/gray_test2.jpg", img2)


def initialize() -> None:
    register("Sift", sift_algorithm)



