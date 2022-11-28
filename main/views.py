from django.shortcuts import render
from main.models import *
from main.forms import *
from main.img2coco import seg2coco
from django.http import JsonResponse
from django.core.files.base import ContentFile
from shapely.geometry import Polygon
import SimpleITK as sitk
from pathlib import Path
import numpy as np
import pyvips
import json
import cv2
import os
import shutil
import copy

pyvips.cache_set_max(0)

# Create your views here.
def home(request):
    dtable = Projects.objects.all().order_by('name')
    alg = Algorithms.objects.all().order_by('name')
    context = {'dtable':dtable,
               'alg': alg}


    return render(request, 'index.html', context)


class MyImage:
    def __init__(self, path):
        self.img = cv2.imread(path,-1)
        self.split = path.split("/")
        self.__name = self.split[-1]

    def __str__(self):
        return self.__name


def saveNP(request):
    dtable = Projects.objects.all().order_by('name')
    alg = Algorithms.objects.all().order_by('name')
    msg = ""


    if request.POST:
        if request.method == "POST":
            form =  ProjectForm(request.POST, request.FILES)
            print("POST:  ",request.POST)
            print("FILES: ", request.FILES)

            if form.is_valid():

                Pname = request.POST['pName']
                algNum = request.POST['algNum']

                file = request.FILES['img1']
                file2  =request.FILES['img2']

                newProject = Projects(name=Pname, image1=file, image2=file2)
                newProject.save()

                createPyramid(f"media/img/fixed/{file}", f"media/img/fixed/{newProject.id}_fix")
                createPyramid(f"media/img/moving/{file2}", f"media/img/moving/{newProject.id}_mov")

                ### Annotations ###

                annType  = request.POST['annotationType']

                if annType == "image" or annType == "npz":
                    nclass  = request.POST['nClasses']
                    annFile  = request.FILES['annImage']
                    classes = []
                    for i in range(1,int(nclass)+1):
                        nameC = request.POST['nameclass'+ str(i)]
                        classes.append(nameC)

                    if annType == "image":

                        imagaPath =  annFile.temporary_file_path()
                        img = MyImage(imagaPath)
                        file_name = str(file2.name)
                        # get shape of image
                        dimensions = img.img.shape
                        if len(dimensions) > 2:
                            height, width, depth = dimensions
                        # if is a binary image
                        elif len(dimensions) == 2 :
                            height, width= dimensions
                            depth = 1
                        image = img.img
                    elif annType == "npz":
                        filePath = annFile.temporary_file_path()
                        npzfile = np.load(filePath)
                        print(npzfile.files)
                        image = npzfile['arr_0']
                        split = filePath.split("/")
                        file_name = split[-1]

                        dimensions = img.img.shape
                        if len(dimensions) > 2:
                            height, width, depth = dimensions
                        elif len(dimensions) == 2:
                            height, width = dimensions
                            depth = 1
                        print(file_name,"-" ,height,"-", width, "-",depth)

                    #create the coco dictionary
                    coco = {}
                    coco["images"] = []
                    coco["annotations"] = []
                    coco["categories"] = []

                    ##create categories
                    for cindx, c in enumerate(classes):
                        coco["categories"].append({"id": cindx + 1, "name": c})



                    if depth == len(classes):
                        ##create images in the dict
                        # As is only one image the id used will be 1
                        indf = 1
                        coco["images"].append({"file_name": file_name, "height": height, "width": width, "id": indf})
                        new_dict = seg2coco(image, classes, coco, indf)

                        newAnn = AnnotationsJson(annotation=new_dict, project= newProject)
                        newAnn.save()

                    else:
                        msg = "each channel is a class, please verify that its number of classes is the same as the depth of the image"


                elif annType == "json":
                    annFile  = request.FILES['annImage']
                    jsonPath = annFile.temporary_file_path()
                    with open(jsonPath) as json_file:
                        new_dict = json.load(json_file)

                    ##in future add a coco format validation
                    newAnn = AnnotationsJson(annotation=new_dict, project=newProject)
                    newAnn.save()




                for i in range(int(algNum)+1):
                    print(i)
                    nameAlg = request.POST['alg'+ str(i)]
                    al = Algorithms.objects.get(name=nameAlg)
                    newResult = Results(algorithm=al, project= newProject)

                    newResult.save()


            else:
                msg = "Please check the fields"

    context = {'dtable': dtable,
               'alg': alg,
               "msg": msg
               }


    return render(request, 'index.html', context)


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

def viewer(request,id_Project, id_viewer=0, id_alg="None"):

    project = Projects.objects.get(id=id_Project)

    if id_alg != "None":
        id_alg = int(id_alg)
        res = Results.objects.get(project=id_Project, algorithm=id_alg)
        features_fix = res.features_fix
        features_mov = res.features_mov
        warpImage = res.warping
        matchingImage = res.line_match
        chessImage =  res.chessboard
        x_val = res.x_chessboard
        y_val = res.y_chessboard


        fixImg = f"/main/media/img/fixed/{project.id}_fix.dzi"
        movImag = f"/main/media/img/moving/{project.id}_mov.dzi"
        if features_fix:
            features_fix = "/main/media/" + features_fix.name[:-4] + ".dzi"
        if features_mov:
            features_mov = "/main/media/" + features_mov.name[:-4] + ".dzi"
        if warpImage:
            warpImage = "/main/media/" + warpImage.name[:-4] + ".dzi"
        if matchingImage:
            matchingImage =  "/main/media/" + matchingImage.name[:-4] + ".dzi"
        if chessImage:
            chessImage =  "/main/media/" + chessImage.name[:-4] + ".dzi"


    else:
        features_fix = ""
        features_mov = ""
        warpImage = ""
        matchingImage = ""
        chessImage = ""
        x_val = ""
        y_val = ""


    alg = Results.objects.filter(project= id_Project)
    ann= AnnotationsJson.objects.filter(project= id_Project)


    ## verify annotations
    if ann:

        categories = []
        ImWidth = 0
        ImWidthWrap = 0
        Ncat = 0
        polygons_mov = []
        polcat_mov = []
        boxArr_mov = []
        polygons_fix = []
        polcat_fix = []
        boxArr_fix = []

        #jsonDict = ann.annotation_wrap
        jsonDict = ann[0].annotation
        jsonDictWrap = res.annotation_wrap

        if jsonDict:
            Ncat = len(jsonDict["categories"])
            categories = jsonDict["categories"]

            arrAnn = jsonDict["annotations"]
            ImWidth =  jsonDict["images"][0]["width"]
            polcat_mov, polygons_mov, boxArr_mov = getPoligonInfo(arrAnn)
            #print(polcat_mov)



        if jsonDictWrap:
            ImWidthWrap =  jsonDictWrap["images"][0]["width"]
            arrAnnWrap = jsonDictWrap["annotations"]

            polcat_fix, polygons_fix, boxArr_fix = getPoligonInfo(arrAnnWrap)

        context = {
            "alg": alg,
            "id_project": int(id_Project),
            "id_viewer": int(id_viewer),
            "id_alg": id_alg,
            "fixImg": fixImg,
            "movImag": movImag,
            "features_fix": features_fix,
            "features_mov": features_mov,
            "warpImage": warpImage,
            "matchingImage": matchingImage,
            "chessImage": chessImage,
            "pol": polygons_mov,
            "polcat": polcat_mov,
            "Ncat": Ncat,
            "ImWidth": ImWidth,
            "ImWidthWrap": ImWidthWrap,
            "boxArr": boxArr_mov,
            "categories": categories,
            "pol_fix": polygons_fix,
            "polcat_fix": polcat_fix,
            "boxAr_fix": boxArr_fix,
            "x_val": x_val,
            "y_val": y_val

        }

    #img1 = project.image1
    #img2 = project.image2
    else:
        context = {
            "alg": alg,
            "id_project": int(id_Project),
            "id_viewer": int(id_viewer),
            "id_alg": id_alg,
            "fixImg": fixImg,
            "movImag": movImag,
            "features_fix": features_fix,
            "features_mov": features_mov,
            "warpImage": warpImage,
            "matchingImage": matchingImage,
            "chessImage": chessImage,
            "x_val": x_val,
            "y_val": y_val

        }


    return render(request, 'viewer.html', context)

def runChessboard(request):
    data = {"msg": "is a get?"}

    if request.GET:
        if request.method == "GET":
            print("por escribir")

    return JsonResponse(data)


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


def deleteProject(request,id_Project):
    msg = ""
    success = False
    if request.POST:
        if request.method == "POST":

            #try:
            #id_Project = request.POST['pId']
            id_Project = str(id_Project)
            project = Projects.objects.get(id=id_Project)
            results = Results.objects.filter(project=id_Project)
            annotations = AnnotationsJson.objects.filter(project=id_Project)
            ImageMediaF = "media/img/"
            pathsFolder = [ImageMediaF + "fixed/" + id_Project + "_fix_files",
                           ImageMediaF + "moving/" + id_Project + "_mov_files"
                           ]


            pathsFiles = [ImageMediaF + "fixed/" + id_Project + "_fix.dzi",
                          ImageMediaF + "moving/" + id_Project + "_mov.dzi",
                          "media/" + project.image1.name,
                          "media/" + project.image2.name,
                          ]

            # append path for every algorithm
            if results:
                for r in results:
                    pathsFolder.append("media/" + r.features_mov.name[:-4] + "_files")
                    pathsFolder.append("media/" + r.features_fix.name[:-4] + "_files")
                    pathsFolder.append("media/" + r.warping.name[:-4] + "_files")
                    pathsFolder.append("media/" + r.line_match.name[:-4] + "_files")
                    pathsFolder.append("media/" + r.chessboard.name[:-4] + "_files")

                    if(r.features_mov.name):
                        pathsFiles.append("media/" + r.features_mov.name[:-4] + ".dzi")
                        pathsFiles.append("media/" + r.features_mov.name)
                    if (r.features_fix.name):
                        pathsFiles.append("media/" + r.features_fix.name[:-4] + ".dzi")
                        pathsFiles.append("media/" + r.features_fix.name)
                    if (r.warping.name):
                        pathsFiles.append("media/" + r.warping.name[:-4] + ".dzi")
                        pathsFiles.append("media/" + r.warping.name)
                    if (r.line_match.name):
                        pathsFiles.append("media/" + r.line_match.name[:-4] + ".dzi")
                        pathsFiles.append("media/" + r.line_match.name)
                    if (r.chessboard.name):
                        pathsFiles.append("media/" + r.chessboard.name[:-4] + ".dzi")
                        pathsFiles.append("media/" + r.chessboard.name)

            for p in pathsFolder:
                if os.path.exists(p):
                    shutil.rmtree(p)

            for pf in pathsFiles:
                if os.path.exists(pf):
                    os.remove(pf)

            annotations.delete()
            results.delete()
            project.delete()

            success =  True
            msg = "the project was successfully removed"

            #except:

             #   data["success"] = False
            # msg = "the project was not successfully removed, please refresh the web page and try again"

    dtable = Projects.objects.all().order_by('name')
    alg = Algorithms.objects.all().order_by('name')

    context = {'dtable': dtable,
               'alg': alg,
               "msg": msg,
               "success":success
               }

    return render(request, 'index.html', context)

def dynamicChessboard(request):

    data = {"success":False}

    if request.GET:
        if request.method == "GET":
            newX = int(request.GET['newX'])
            newY = int(request.GET['newY'])
            id_alg = int(request.GET['id_alg'])
            id_proj = int(request.GET['id_project'])

            result = Results.objects.get(project=id_proj, algorithm=id_alg)

            wrapping = result.warping.name
            project = Projects.objects.get(id=id_proj)
            fix_path = project.image1.name

            wrapping_img  = cv2.imread("media/" + wrapping)
            fix_image = cv2.imread("media/" + fix_path)

            ##fix
            transformed_rgb = cv2.cvtColor(wrapping_img, cv2.COLOR_BGR2RGB)
            img_color2_rgb = cv2.cvtColor(fix_image, cv2.COLOR_BGR2RGB)

            img2_ori_stk = sitk.GetImageFromArray(transformed_rgb, isVector=True)
            img1_stk = sitk.GetImageFromArray(img_color2_rgb, isVector=True)

            # img1_stk = sitk.ReadImage("media/" + im1Name)

            img2_ori_stk.SetSpacing([1.0, 1.0])
            img1_stk.SetSpacing([1.0, 1.0])

            image_list = sitk.CheckerBoard(img2_ori_stk, img1_stk, [newX, newY, newY])
            ##convert itk to array
            array = sitk.GetArrayFromImage(image_list)
            array_rgb = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

            savingModel(result.chessboard, array_rgb, f"chess_{id_proj}_{result.algorithm.name}.jpg")


            #createPyramid("media/" + al.chessboard.name, "media/" + al.chessboard.name[:-4])

            result.x_chessboard = newX
            result.y_chessboard = newY

            result.save()
            createPyramid("media/" + result.chessboard.name, "media/" + result.chessboard.name[:-4])
            data = {"success": True}





    return JsonResponse(data)


def runAlg(request):
    res = {"alg":[],"result":[]}
    resultsPath = "media/img/results"
    if request.POST:
        if request.method == "POST":

            id_Project = request.POST['pId']
            project = Projects.objects.get(id=id_Project)
            algorithms = Results.objects.filter(project=id_Project)
            im1Name = project.image1.name
            im2Name = project.image2.name

            print(im1Name)

            for al in algorithms:
                alg = al.algorithm.name

                img_color = cv2.imread("media/" + im2Name)
                img_color2 = cv2.imread("media/"+ im1Name)

                #createPyramid(f"media/{im1Name}", f"media/img/fixed/{id_Project}_fix")
                #createPyramid(f"media/{im2Name}", f"media/img/moving/{id_Project}_mov")


                img = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
                img2 = cv2.cvtColor(img_color2, cv2.COLOR_BGR2GRAY)

                height, width, _ = img_color2.shape

                # feature extractor
                if (alg == "Sift"):
                    fExt = cv2.xfeatures2d.SIFT_create()

                elif (alg == "Sift+Colorinvertion"):
                    fExt = cv2.xfeatures2d.SIFT_create()
                    gray_negative = abs(255 - img2)
                    #img_flip_ud = cv2.flip(gray_negative, 1)
                    #img_color2 = cv2.flip(img_color2, 1)
                    #img2 = img_flip_ud
                    img2 = gray_negative

                elif (alg == "ORB"):

                    fExt = cv2.ORB_create(nfeatures=1000)
                elif (alg == "BRIEF"):
                    fExt = cv2.features2d.BriefDescriptorExtractor()
                elif (alg == "BoostDesc"):
                    fExt = cv2.features2d.BoostDesc()

                res["alg"].append(alg)

                keypoints, descriptors = fExt.detectAndCompute(img, None)
                keypoints2, descriptors2 = fExt.detectAndCompute(img2, None)

                keyDraw1 = cv2.drawKeypoints(img, keypoints, None)
                keyDraw2 = cv2.drawKeypoints(img2, keypoints2, None)

                #Path(f"{resultsPath}/{id_Project}/").mkdir(parents=True, exist_ok=True)

                # save in model opencv images
                #keyDraw1= reduceImage(keyDraw1)
                #keyDraw2= reduceImage(keyDraw2)

                savingModel(al.features_mov, keyDraw1, f"features_{id_Project}_{alg}_moving.jpg")
                savingModel(al.features_fix, keyDraw2, f"features_{id_Project}_{alg}_fixing.jpg")


                createPyramid("media/" +al.features_mov.name, "media/" +al.features_mov.name[:-4])
                createPyramid("media/" +al.features_fix.name, "media/" + al.features_fix.name[:-4])

                FLAN_INDEX_KDTREE = 0
                index_params = dict(algorithm=FLAN_INDEX_KDTREE, trees=8)
                search_params = dict(checks=1000)

                #flann = cv2.FlannBasedMatcher(index_params, search_params)
                flann = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)

                matches = flann.knnMatch(descriptors, descriptors2, k=8)

                good_matches = []

                for m1, m2, *_ in matches:
                    # good_matches.append(m1)

                    if m1.distance < 0.65 * m2.distance:
                        good_matches.append(m1)

                matches = good_matches


                lineMatch = cv2.drawMatches(img_color, keypoints, img_color2, keypoints2, matches[:50], None, flags=2)
                #lineMatch = reduceImage(lineMatch)

                savingModel(al.line_match, lineMatch, f"lineMatch_{id_Project}_{alg}.jpg")
                createPyramid("media/" +al.line_match.name,"media/" +al.line_match.name[:-4])

                no_of_matches = len(matches)

                # Define empty matrices of shape no_of_matches * 2.
                p1 = np.zeros((no_of_matches, 2))
                p2 = np.zeros((no_of_matches, 2))

                for i, match in enumerate(matches):
                    p1[i, :] = keypoints[match.queryIdx].pt
                    p2[i, :] = keypoints2[match.trainIdx].pt



                if no_of_matches > 3:
                    homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)
                    transformed_img = cv2.warpPerspective(img_color, homography, (width, height))
                    #print("mask: ", mask)
                    #print("Homography: ", homography)

                    #transformed_img_2 = reduceImage(transformed_img)

                    savingModel(al.warping, transformed_img, f"warp_{id_Project}_{alg}.jpg")



                    createPyramid("media/" +al.warping.name,"media/" +al.warping.name[:-4])

                    transformed_rgb = cv2.cvtColor(transformed_img, cv2.COLOR_BGR2RGB)
                    img_color2_rgb = cv2.cvtColor(img_color2, cv2.COLOR_BGR2RGB)

                    img2_ori_stk = sitk.GetImageFromArray(transformed_rgb, isVector=True)
                    img1_stk = sitk.GetImageFromArray(img_color2_rgb, isVector=True)


                    #img1_stk = sitk.ReadImage("media/" + im1Name)



                    img2_ori_stk.SetSpacing([1.0, 1.0])
                    img1_stk.SetSpacing([1.0, 1.0])

                    image_list = sitk.CheckerBoard(img2_ori_stk, img1_stk, [4, 4, 4])
                    ##convert itk to array
                    array = sitk.GetArrayFromImage(image_list)
                    array_rgb = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

                    #array_rgb = reduceImage(array_rgb)

                    savingModel(al.chessboard, array_rgb, f"chess_{id_Project}_{alg}.jpg")
                    createPyramid("media/" +al.chessboard.name,"media/" +al.chessboard.name[:-4])


                    ##modify poligons

                    ann = AnnotationsJson.objects.filter(project=id_Project)
                    if ann:
                        jsonDict = ann[0].annotation
                        arrAnn = jsonDict["annotations"]
                        newDict = copy.deepcopy(jsonDict)

                        for indxAnn, an in enumerate(arrAnn):
                            seg = an["segmentation"]
                            newseg = []
                            for indxSeg, s in enumerate(seg):
                                print("indxAnn: ", indxAnn, " indxSeg: ", indxSeg)
                                #poly = np.array(s).reshape((int(len(s) / 2), 2))
                                #print("poly: ", poly)
                                #print("s: ", s)
                                #dor product betwen homography and a matrix
                                # x
                                # y
                                # 1
                                #pol_tuplas = [(s[i],s[i+1]) for i in range(0, len(s), 2)]
                                #print("area1: ", Polygon(pol_tuplas).area)


                                matrixDot = [np.dot(homography, [[s[i]], [s[i + 1]], [1]]) for i in range(0, len(s), 2)]
                                newPoli = []
                                for i in matrixDot:
                                    newPoli.append(float(i[0] / i[2]))
                                    newPoli.append(float(i[1] / i[2]))
                                pol_tuplas2 = [(newPoli[i], newPoli[i + 1]) for i in range(0, len(newPoli), 2)]
                                #print("area2: ", Polygon(pol_tuplas2).area)
                                newDict["annotations"][indxAnn]["area"] = Polygon(pol_tuplas2).area
                                bounds_seg = Polygon(pol_tuplas2).bounds
                                newDict["annotations"][indxAnn]["bbox"] = [bounds_seg[0],bounds_seg[1],bounds_seg[2]-bounds_seg[0],bounds_seg[3]-bounds_seg[1]]


                                #print("bounds_Shap: ", Polygon(pol_tuplas2).bounds)

                                newseg.append(newPoli)

                                #polygons.append(poly)
                            newDict["annotations"][indxAnn]["segmentation"] = newseg

                            ## different way to get the bbox
                            #box_coord = an["bbox"]
                            #print("bbox1: ", box_coord)
                            #bbox_points = [np.dot(homography, [[box_coord[0]],[box_coord[1]] , [1]]) ,  np.dot(homography, [[box_coord[0] + box_coord[2]],[box_coord[1] + box_coord[3]] , [1]]) ]
                            #box_coord = [[float(i[0] / i[2]) , float(i[1] / i[2])]  for i in bbox_points]
                            #newBbox = [ box_coord[0][0], box_coord[0][1], box_coord[1][0] - box_coord[0][0], box_coord[1][1] - box_coord[0][1]]
                            #print("bbox2: ", newBbox)



                            #newAnn.append(an)

                        #jsonDict["annotations"] = newAnn
                        #jsonDict["bbox"] = newBbox



                        #change this section for batch (now is only for one image)
                        newDict["images"] = [{"file_name": im1Name, "height": height , "width": width, "id": 1}]

                        #print(jsonDict["annotations"])

                        al.annotation_wrap = newDict
                        al.save()



                    res["result"].append(True)
                else:
                    res["result"].append(False)
                data = {"result": res}

    return JsonResponse(data)


