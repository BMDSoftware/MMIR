import os
import cv2
import pyvips
import numpy as np
from pathlib import Path
import shutil
from django.core.files.base import ContentFile

class MyImage:
    def __init__(self, path):
        self.img = cv2.imread(path,-1)
        self.split = path.split("/")
        self.__name = self.split[-1]

    def __str__(self):
        return self.__name


def savingModel(modelPar, image, strName):
    _, buf = cv2.imencode('.jpg', image)
    savingImage = ContentFile(buf.tobytes())

    modelPar.save(strName , savingImage)

def createPyramid (cvImagePath,pyramidPath):

    if os.path.exists(pyramidPath+".dzi"):
        os.remove(pyramidPath+".dzi")

    if os.path.exists(pyramidPath+"_files"):
        shutil.rmtree(pyramidPath+"_files",ignore_errors=True)

    image = pyvips.Image.new_from_file(cvImagePath)
    folderName = pyramidPath.split("/")

    image.dzsave(
        cvImagePath,
        basename=folderName[-1],
        suffix=".png",
        tile_size=1024,
        overlap=0,
        depth="onepixel",
        properties=False
    )


def reduceImage(img):
    height, width, _ = img.shape
    #scale_percentage using 2048 as width
    sp = (2048*100)/width
    NewWidth = int(width * sp / 100)
    NewHeight = int(height * sp / 100)
    dim = (NewWidth, NewHeight)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized

def getPoligonInfo(AnnArray):
    polygons = []
    polcat = []
    bboxArr = []
    for an in AnnArray:
        seg = an["segmentation"]
        polcat.append(an["category_id"])
        bboxArr.append(an["bbox"])


        for s in seg:
            poly = np.array(s).reshape((int(len(s) / 2), 2))
            polygons.append(poly)

    return polcat, polygons, bboxArr