from django.shortcuts import render
from main.models import *
from main.forms import *
from django.http import JsonResponse
from django.core.files.base import ContentFile
import SimpleITK as sitk
from pathlib import Path
import numpy as np
import pyvips
import json
import cv2



# Create your views here.
def home(request):
    dtable = Projects.objects.all().order_by('name')
    alg = Algorithms.objects.all().order_by('name')
    context = {'dtable':dtable,
               'alg': alg}


    return render(request, 'index.html', context)


def saveNP(request):
    dtable = Projects.objects.all().order_by('name')
    alg = Algorithms.objects.all().order_by('name')
    msg = ""


    if request.POST:
        if request.method == "POST":
            form =  ProjectForm(request.POST, request.FILES)

            if form.is_valid():

                Pname = request.POST['pName']
                algNum = request.POST['algNum']

                file = request.FILES['img1']
                file2  =request.FILES['img2']


                newProject = Projects(name= Pname,image1=file, image2=file2)
                newProject.save()

                createPyramid(f"media/img/fixed/{file}", f"media/img/fixed/{newProject.id}_fix")
                createPyramid(f"media/img/moving/{file2}", f"media/img/moving/{newProject.id}_mov")

                print(request.POST)
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




def viewer(request,id_Project, id_viewer=0, id_alg="None"):

    if id_alg != "None":
        id_alg = int(id_alg)
        res = Results.objects.get(project=id_Project, algorithm=id_alg)
        features_fix = res.features_fix
        features_mov = res.features_mov
        warpImage = res.warping
        matchingImage = res.line_match
        chessImage =  res.chessboard


    else:
        features_fix = None
        features_mov = None
        warpImage = None
        matchingImage = None
        chessImage = None

    project = Projects.objects.get(id=id_Project)
    alg = Results.objects.filter(project= id_Project)

    #img1 = project.image1
    #img2 = project.image2


    context= {
                "alg":alg,
                "id_project":int(id_Project),
                "id_viewer":int(id_viewer),
                "id_alg":id_alg,
                "fixImg": f"/main/media/img/fixed/{project.id}_fix.dzi",
                "movImag": f"/main/media/img/moving/{project.id}_mov.dzi",
                "features_fix": features_fix,
                "features_mov": features_mov,
                "warpImage": warpImage,
                "matchingImage": matchingImage,
                "chessImage": chessImage

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
                    img_flip_ud = cv2.flip(gray_negative, 1)
                    img_color2 = cv2.flip(img_color2, 1)
                    img2 = img_flip_ud

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
                keyDraw1_2= reduceImage(keyDraw1)
                keyDraw2_2= reduceImage(keyDraw2)

                savingModel(al.features_mov, keyDraw1_2, f"features_{id_Project}_{alg}_moving.jpg")
                savingModel(al.features_fix, keyDraw2_2, f"features_{id_Project}_{alg}_fixing.jpg")

                #createPyramid(f"{resultsPath}/f_mov/features_{id_Project}_{alg}_moving.jpg", f"{resultsPath}/f_mov/{id_Project}_{alg}_moving")
                #createPyramid(f"{resultsPath}/f_fix/features_{id_Project}_{alg}_fixing.jpg", f"{resultsPath}/f_fix/{id_Project}_{alg}_fixing")

                FLAN_INDEX_KDTREE = 0
                index_params = dict(algorithm=FLAN_INDEX_KDTREE, trees=8)
                search_params = dict(checks=1000)

                flann = cv2.FlannBasedMatcher(index_params, search_params)
                matches = flann.knnMatch(descriptors, descriptors2, k=5)

                good_matches = []

                for m1, m2, *_ in matches:
                    # good_matches.append(m1)

                    if m1.distance < 0.65 * m2.distance:
                        good_matches.append(m1)

                matches = good_matches


                lineMatch = cv2.drawMatches(img_color, keypoints, img_color2, keypoints2, matches[:50], None, flags=2)
                lineMatch_2 = reduceImage(lineMatch)

                savingModel(al.line_match, lineMatch_2, f"lineMatch_{id_Project}_{alg}.jpg")
               # createPyramid(f"{resultsPath}/l_match/lineMatch_{id_Project}_{alg}.jpg",
                #              f"{resultsPath}/l_match/{id_Project}_{alg}_lineMatch")

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

                    transformed_img_2 = reduceImage(transformed_img)

                    savingModel(al.warping, transformed_img_2, f"warp_{id_Project}_{alg}.jpg")



                    #createPyramid(f"{resultsPath}/warp/warp_{id_Project}_{alg}.jpg",
                     #             f"{resultsPath}/warp{id_Project}_{alg}_warp")

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

                    array_rgb = reduceImage(array_rgb)



                    savingModel(al.chessboard, array_rgb, f"chess_{id_Project}_{alg}.jpg")
                    #createPyramid(f"{resultsPath}/chess/chess_{id_Project}_{alg}.jpg",
                     #             f"{resultsPath}/chess/{id_Project}_{alg}_chess")


                    res["result"].append(True)
                else:
                    res["result"].append(False)
                data = {"result": res}

    return JsonResponse(data)


