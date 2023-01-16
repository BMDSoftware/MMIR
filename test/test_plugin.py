
# test plugins

#from main.plugin_register import *
#from main.plugin_loader import *
from algorithms import plugin_loader, plugin_register

import json

def main()-> None:
    ##load images that will be used to test an algorithm
    #img_mov = cv2.imread("../media/img/fixed/ID_000801_ContrastAdjust.png")
    #img_fix = cv2.imread("../media/img/fixed/ID_008.png")

    # register plugins
    #register("Sift", sift_algorithm)

    with open("./plugins/plugins_list.json") as file:
        data = json.load(file)
        # load the plugins
        plugin_loader.load_plugins(data["plugins"])

        print(plugin_register.getAlgNames())
        ## crear objeto del plugin deseado
        objeto = plugin_register.create("Sift",5 , 2)
        print(objeto.__dict__)
        print(dir(objeto))
        objeto.run()
        print(objeto.name)
        print(objeto.name == "Orb")
        print(objeto.name == "Sift")



if __name__ == "__main__":
    main()