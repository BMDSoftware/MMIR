import cv2
import numpy as np
from os import listdir
from os.path import isfile, join

def concat_tile(im_list_2d):
    merg_im = np.vstack([np.hstack(im_list_h) for im_list_h in im_list_2d])


    return merg_im

def build_Array(list_files, nCol, str_template, image_dim):
    len_files = len(list_files)
    rows = int(np.ceil(len_files / nCol))
    buildArray= []

    for i in range(1,rows+1):
        buildArray.append([])
        for j in range(1,nCol+1):
            Inumber = j + (nCol * (i-1))
            if(Inumber < len_files + 1):
                img = cv2.imread(f"image/" + str_template[0] + str(Inumber) + str_template[1] ,-1)

                buildArray[i-1].append(img)
                #buildArray[i-1].append(1)
            else:
                img = np.zeros(image_dim)
                #print(img.shape)
                buildArray[i - 1].append(img)
                #buildArray[i - 1].append(0)

    mergeImages = concat_tile(buildArray)
    #mergeImages = buildArray
    return mergeImages

Files = [f for f in listdir("Image") if isfile(join("Image", f))]


Image_per_column = 12

str_name = 'ImageFileName*.jpg'
template = str_name.split('*')

#print(template)

dim = (1024, 1280)
im_array = build_Array(Files, Image_per_column, template, dim)



cv2.imwrite("test_files/ramman_image.jpg", im_array)
#print(np.ceil(len_files/Image_per_column))
#print(len_files % Image_per_column)

