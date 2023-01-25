from django.test import TestCase
# test plugins

#from main.plugin_register import *
#from main.plugin_loader import *
from algorithmsPlugin import plugin_loader, plugin_register
import cv2

import json

def main()-> None:
    ##load images that will be used to test an algorithm
    img_fix = cv2.imread("../media/img/fixed/15/ID_000801_ContrastAdjust.png")
    img_mov = cv2.imread("../media/img/moving/15/ID_008.png")

    # register plugins
    #register("Sift", sift_algorithm)

    with open("./plugins/plugins_list.json") as file:
        data = json.load(file)
        # load the plugins
        plugin_loader.load_plugins(data["plugins"])

        print(plugin_register.getAlgNames())
        ## crear objeto del plugin deseado
        objeto = plugin_register.create("Sift",img_mov , img_fix)
        #print(objeto.__dict__)
        #print(dir(objeto))
        res = objeto.run()
        print(res["warping"])
        print(objeto.name)
        print(objeto.name == "Orb")
        print(objeto.name == "Sift")


        #cv2.imwrite("../test/test_files/gray_test1.jpg", img)
        #cv2.imwrite("../test/test_files/gray_test2.jpg", img2)



if __name__ == "__main__":
    main()