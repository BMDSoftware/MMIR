from django.shortcuts import render
from main.models import *
from main.forms import *
from django.http import JsonResponse
from django.core.files.base import ContentFile
import SimpleITK as sitk
import json
import cv2
import numpy as np
from pathlib import Path

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

    img1 = project.image1
    img2 = project.image2


    context= {
                "alg":alg,
                "id_project":int(id_Project),
                "id_viewer":int(id_viewer),
                "id_alg":id_alg,
                "fixImg": img1,
                "movImag": img2,
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

def runAlg(request):
    res = {"alg":[],"result":[]}
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


                img = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
                img2 = cv2.cvtColor(img_color2, cv2.COLOR_BGR2GRAY)

                height, width, _ = img_color2.shape

                # feature extractor
                if (alg == "Sift"):
                    fExt = cv2.xfeatures2d.SIFT_create()

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

                Path(f"media/img/results/{id_Project}").mkdir(parents=True, exist_ok=True)

                #save in model opencv images
                _, bufMov = cv2.imencode('.jpg', keyDraw1)
                _, bufFix = cv2.imencode('.jpg', keyDraw2)
                movingImage = ContentFile(bufMov.tobytes())
                fixingImage = ContentFile(bufFix.tobytes())

                al.features_mov.save(f"features_{id_Project}_{alg}_moving.jpg",movingImage)
                al.features_fix.save(f"features_{id_Project}_{alg}_fixing.jpg",fixingImage)

                #cv2.imwrite(f"media/img/results/{id_Project}/features_{alg}_moving.jpg", keyDraw1)
                #cv2.imwrite(f"media/img/results/{id_Project}/features_{alg}_fixing.jpg", keyDraw2)

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

                _, bufMatch = cv2.imencode('.jpg', lineMatch)

                matchingImage = ContentFile(bufMatch.tobytes())

                al.line_match.save(f"lineMatch_{id_Project}_{alg}.jpg", matchingImage)

                #cv2.imwrite(f"media/img/results/{id_Project}/lineMatch_{alg}.jpg", lineMatch)

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
                    _, bufWarp = cv2.imencode('.jpg', transformed_img)

                    warpImage = ContentFile(bufWarp.tobytes())

                    al.warping.save(f"warp_{id_Project}_{alg}.jpg", warpImage)

                    #cv2.imwrite(f"media/img/results/{id_Project}/warp_{alg}.jpg", transformed_img)



                    img2_ori_stk = sitk.ReadImage(f"media/img/results/warp/warp_{id_Project}_{alg}.jpg")
                    img1_stk = sitk.ReadImage("media/" + im1Name)

                    img2_ori_stk.SetSpacing([1.0, 1.0])
                    img1_stk.SetSpacing([1.0, 1.0])

                    image_list = sitk.CheckerBoard(img2_ori_stk, img1_stk, [4, 4, 4])
                    ##convert itk to array
                    array = sitk.GetArrayFromImage(image_list)
                    array_rgb = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

                    _, bufChess = cv2.imencode('.jpg', array_rgb)
                    chessImage = ContentFile(bufChess.tobytes())

                    al.chessboard.save(f"chess_{id_Project}_{alg}.jpg", chessImage)


                    res["result"].append(True)
                else:
                    res["result"].append(False)
                data = {"result": res}

    return JsonResponse(data)


