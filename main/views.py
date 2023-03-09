from django.shortcuts import render
from main.models import *
from main.forms import *
from main.img2coco import seg2coco
from main.utils import *
from django.http import JsonResponse
from django.core.files.base import ContentFile
from main.algorithmsPlugin import plugin_loader, plugin_register
from django.http import HttpResponse
from shapely.geometry import Polygon
import SimpleITK as sitk
from pathlib import Path
import numpy as np
import pyvips
import json
import cv2
import os, io, zipfile, requests
import shutil
import copy
import sys

pyvips.cache_set_max(0)


if not any(elem in sys.argv for elem in ('makemigrations', 'migrate')):

    with open("main/plugins/plugins_list.json") as file:
        data_plugins = json.load(file)
        # load the plugins
        print("Loading plugins ...")
        plugin_loader.load_plugins(data_plugins["plugins"])
        plugins_names = plugin_register.getAlgNames()
        print("add plugins to the db ...")
        for plugin in plugins_names:

            pg_db = Algorithms.objects.filter(name=plugin)
            if not pg_db:
                newAlg = Algorithms(name=plugin)
                newAlg.save()

        print("plugins added")
        # DELETE when is not in the plugin list
        db_Algs = Algorithms.objects.all()
        for db_al in db_Algs:
            if db_al.name not in plugins_names:
                db_al.delete()


# Create your views here.
def home(request):
    dtable = Projects.objects.all().order_by('name')
    alg = Algorithms.objects.all().order_by('name')
    context = {'dtable':dtable,
               'alg': alg}


    return render(request, 'index.html', context)


def downloadFiles(request,id_Project):
    project = Projects.objects.get(id=id_Project)
    registration_images = Registration_Images.objects.filter(project=project)
    wrap_ann = AnnotationswrapJson.objects.filter(project=project)
    fileList = []
    jsonList = []
    for regImage in registration_images:
        results_obj = Results.objects.filter(Registration_Images=regImage)
        for res in results_obj:
            warp_image = res.warping
            json_annotation = res.annotation_wrap
            if warp_image != "":

                fileList.append("media/"+ warp_image.name)
    for wAnn in wrap_ann:
        if json_annotation != "{}":
                jsonList.append({
                    "name":f"annotation___Project_{wAnn.project.name}__Alg_{wAnn.algorithm.name}.json",
                    "dict":wAnn.annotation})
    buffer = io.BytesIO()


    with zipfile.ZipFile(buffer , 'w') as file_zip:
        for fileURl in fileList:

            #file_data = requests.get(fileURl).content
            split = fileURl.split("/")
            arcname = split[-1]
            file_zip.write(fileURl,arcname=arcname)
        for jsonfile in jsonList:
            json_string = json.dumps(jsonfile["dict"], indent=4)
            file_zip.writestr(jsonfile["name"], json_string)

    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = f'attachment; filename=Files_project_{id_Project}.zip'
    return response



def saveNP(request):
    dtable = Projects.objects.all().order_by('name')
    alg = Algorithms.objects.all().order_by('name')
    msg = ""


    if request.POST:
        if request.method == "POST":
            form =  ProjectForm(request.POST, request.FILES)
            #print("POST:  ",request.POST)
            #print("FILES: ", request.FILES)

            if form.is_valid():

                Pname = request.POST['pName']
                algNum = request.POST['algNum']

                newProject = Projects(name=Pname)
                newProject.save()

                FixList = request.FILES.getlist('img1')
                MovList =request.FILES.getlist('img2')

                if len(FixList) == len(MovList):
                    for i in range(len(FixList)):
                        fileFix = FixList[i]
                        fileMov = MovList[i]

                        NewRegImages = Registration_Images(image1=fileFix,image2=fileMov, project=newProject)
                        NewRegImages.save()

                        createPyramid(f"media/img/fixed/{newProject.id}/{fileFix}", f"media/img/fixed/{newProject.id}/{NewRegImages.id}_fix")
                        createPyramid(f"media/img/moving/{newProject.id}/{fileMov}", f"media/img/moving/{newProject.id}/{NewRegImages.id}_mov")

                        for j in range(int(algNum) + 1):
                            nameAlg = request.POST['alg' + str(j)]
                            al = Algorithms.objects.get(name=nameAlg)
                            newResult = Results(algorithm=al, Registration_Images=NewRegImages)

                            newResult.save()

                    ### Annotations ###

                    annType  = request.POST['annotationType']

                    if annType == "image" or annType == "npz":
                        nclass = request.POST['nClasses']
                        annList = request.FILES.getlist('annImage')
                        classes = []
                        for i in range(1, int(nclass) + 1):
                             nameC = request.POST['nameclass'+ str(i)]
                             classes.append(nameC)
                        # create the coco dictionary
                        coco = {}
                        coco["images"] = []
                        coco["annotations"] = []
                        coco["categories"] = []

                        ##create categories
                        for cindx, c in enumerate(classes):
                            coco["categories"].append({"id": cindx + 1, "name": c})

                        # annotation id
                        idAnn = 0

                        for i in range(len(annList)):
                            if annType == "image":
                                fileMov = MovList[i]
                                annFile = annList[i]

                                imagaPath =  annFile.temporary_file_path()
                                img = MyImage(imagaPath)
                                file_name = str(fileMov.name)
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
                                fileMov = MovList[i]
                                annFile = annList[i]
                                filePath = annFile.temporary_file_path()
                                npzfile = np.load(filePath)
                                #print(npzfile.files)
                                image = npzfile['arr_0']
                                #split = filePath.split("/")
                                file_name = str(fileMov.name)

                                dimensions = image.shape
                                if len(dimensions) > 2:
                                    height, width, depth = dimensions
                                elif len(dimensions) == 2:
                                    height, width = dimensions
                                    depth = 1
                                #print(file_name,"-" ,height,"-", width, "-",depth)

                            if depth == len(classes):
                                ##create images in the dict
                                # image id
                                indf = i + 1
                                coco["images"].append({"file_name": file_name, "height": height, "width": width, "id": indf})

                                coco, idAnn = seg2coco(image, classes, coco, indf, idAnn)
                                saveAnn = True

                            else:
                                msg = "each channel is a class, please verify that its number of classes is the same as the depth of the image"
                                saveAnn = False


                        if saveAnn:
                            newAnn = AnnotationsJson(annotation=coco, project=newProject)
                            newAnn.save()

                    elif annType == "json":
                        annFile  = request.FILES['annImage']
                        jsonPath = annFile.temporary_file_path()
                        with open(jsonPath) as json_file:
                            new_dict = json.load(json_file)

                        ##in future add a coco format validation
                        newAnn = AnnotationsJson(annotation=new_dict, project=newProject)
                        newAnn.save()



                else:
                    msg = "Moving and Fix Folder must have the same number of files."




            else:
                msg = "Please check the fields"

    context = {'dtable': dtable,
               'alg': alg,
               "msg": msg
               }


    return render(request, 'index.html', context)




def viewer(request,id_Project, id_viewer , id_reg_img, id_alg="None"):

    project = Projects.objects.get(id=id_Project)
    reg_img = Registration_Images.objects.get(id=id_reg_img)



    fixImg = f"/main/media/img/fixed/{project.id}/{id_reg_img}_fix.dzi"
    movImag = f"/main/media/img/moving/{project.id}/{id_reg_img}_mov.dzi"

    if id_alg != "None":
        id_alg = int(id_alg)
        res = Results.objects.get(Registration_Images=reg_img, algorithm=id_alg)
        features_fix = res.features_fix
        features_mov = res.features_mov
        warpImage = res.warping
        matchingImage = res.line_match
        chessImage =  res.chessboard
        x_val = res.x_chessboard
        y_val = res.y_chessboard


        #fixImg = f"/main/media/img/fixed/{project.id}/{id_fix}_fix.dzi"
        #movImag = f"/main/media/img/moving/{project.id}/{id_mov}_mov.dzi"
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


    alg = Results.objects.filter(Registration_Images=reg_img)
    reg_batch = Registration_Images.objects.filter(project= project)
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

        mov_filename = reg_img.image2.name
        split = mov_filename.split("/")
        mov_filename = split[-1]
        fix_filename = reg_img.image1.name
        split = fix_filename.split("/")
        fix_filename = split[-1]
        #jsonDict = ann.annotation_wrap
        jsonDict = ann[0].annotation
        jsonDictWrap = res.annotation_wrap

        #print("mov_filename: ", fix_filename)

        if jsonDict:
            Ncat = len(jsonDict["categories"])
            categories = jsonDict["categories"]

            dictImages = [im for im in jsonDict["images"] if im["file_name"] == mov_filename]
            id_image = dictImages[0]["id"]
            #arrAnn = jsonDict["annotations"]
            arrAnn = [a for a in jsonDict["annotations"] if a["image_id"] == id_image ]
            ImWidth =  int(dictImages[0]["width"])
            polcat_mov, polygons_mov, boxArr_mov = getPoligonInfo(arrAnn)
            #print(polcat_mov)



        if jsonDictWrap:
            ann_wrap_json = jsonDictWrap.annotation
            dictImages = [im for im in ann_wrap_json["images"] if im["file_name"] == fix_filename]
            id_image = dictImages[0]["id"]

            ImWidthWrap =  int(dictImages[0]["width"])
            arrAnnWrap = [a for a in ann_wrap_json["annotations"] if a["image_id"] == id_image ]

            polcat_fix, polygons_fix, boxArr_fix = getPoligonInfo(arrAnnWrap)

        context = {
            "alg": alg,
            "id_project": int(id_Project),
            "id_reg_img": id_reg_img,
            "reg_batch":reg_batch,
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
            "id_reg_img":id_reg_img,
            "reg_batch": reg_batch,
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





def deleteProject(request,id_Project):
    msg = ""
    success = False
    if request.POST:
        if request.method == "POST":

            #try:
            #id_Project = request.POST['pId']
            id_Project = str(id_Project)
            project = Projects.objects.get(id=id_Project)
            reg = Registration_Images.objects.filter(project = id_Project)
            #results = Results.objects.filter(project=id_Project)
            annotations = AnnotationsJson.objects.filter(project=id_Project)
            annotationsWrap = AnnotationswrapJson.objects.filter(project=id_Project)
            ImageMediaF = "media/img/"
            pathsFolder = [ImageMediaF + "fixed/" + id_Project,
                           ImageMediaF + "moving/" + id_Project
                           ]


            #pathsFiles = [ImageMediaF + "fixed/" + id_Project + "_fix.dzi",
             #             ImageMediaF + "moving/" + id_Project + "_mov.dzi",
                         # "media/" + project.image1.name,
                         # "media/" + project.image2.name,
              #            ]
            for re in reg:
                results = Results.objects.filter(Registration_Images=re)
                # append path for every algorithm
                #pathsFiles.append("media/" + re.image1.name)
                #pathsFiles.append("media/" + re.image2.name)
                if results:

                    pathsFolder.append("media/img/results/chess/" + id_Project)
                    pathsFolder.append("media/img/results/feature_fix/" + id_Project)
                    pathsFolder.append("media/img/results/feature_mov/" + id_Project)
                    pathsFolder.append("media/img/results/line_match/" + id_Project)
                    pathsFolder.append("media/img/results/warp/" + id_Project)
                for r in results:
                    r.delete()
                re.delete()

            for p in pathsFolder:
                if os.path.exists(p):
                    shutil.rmtree(p)



            annotations.delete()
            annotationsWrap.delete()
            project.delete()

            success =  True
            msg = "the project has been successfully removed"

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
            id_reg_img = int(request.GET['id_reg'])

            result = Results.objects.get(Registration_Images=id_reg_img, algorithm=id_alg)

            wrapping = result.warping.name
            #reg = Registration_Images.objects.get(project__id=id_proj)
            fix_path = result.Registration_Images.image1.name

            wrapping_img  = cv2.imread("media/" + wrapping, cv2.IMREAD_UNCHANGED)
            fix_image = cv2.imread("media/" + fix_path, cv2.IMREAD_UNCHANGED)

            ##fix
            transformed_rgb = cv2.cvtColor(wrapping_img, cv2.COLOR_BGR2RGB)
            ### temporal code 4-channel image
            #fix_image[:, :, 0] = fix_image[:, :, 3]
            #fix_image[:, :, 1] = fix_image[:, :, 3]
            #fix_image[:, :, 2] = fix_image[:, :, 3]

            ### end temporal code
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

            savingModel(result.chessboard, array_rgb, f"chess_{id_proj}_{result.Registration_Images.id}_{result.algorithm.name}.jpg")


            #createPyramid("media/" + al.chessboard.name, "media/" + al.chessboard.name[:-4])

            result.x_chessboard = newX
            result.y_chessboard = newY

            result.save()
            createPyramid("media/" + result.chessboard.name, "media/" + result.chessboard.name[:-4])
            data = {"success": True}





    return JsonResponse(data)


def runAlg(request):
    res = {"alg":[],"result":[]}
    #resultsPath = "media/img/results"
    if request.POST:
        if request.method == "POST":

            id_Project = request.POST['pId']
            project = Projects.objects.get(id=id_Project)
            reg_images =  Registration_Images.objects.filter(project=id_Project)

            for reg in reg_images:
                algorithms = Results.objects.filter(Registration_Images=reg)


                im1Name = reg.image1.name
                im2Name = reg.image2.name



                for al in algorithms:
                    alg = al.algorithm.name

                    img_color = cv2.imread("media/" + im2Name, cv2.IMREAD_UNCHANGED)
                    #print(img_color.shape)
                    img_color2 = cv2.imread("media/"+ im1Name, cv2.IMREAD_UNCHANGED)
                    #print(img_color2.shape)

                    plugin_obj = plugin_register.create(alg, img_color2, img_color)

                    alg_res = plugin_obj.run()

                    if alg_res["f_mov"] is not None:
                        savingModel(al.features_mov, alg_res["f_mov"], f"features_{id_Project}_{reg.id}_{alg}_moving.jpg")
                        createPyramid("media/" + al.features_mov.name, "media/" + al.features_mov.name[:-4])

                    if alg_res["f_fix"] is not None:
                        savingModel(al.features_fix, alg_res["f_fix"], f"features_{id_Project}_{reg.id}_{alg}_fixing.jpg")
                        createPyramid("media/" + al.features_fix.name, "media/" + al.features_fix.name[:-4])

                    if alg_res["lineMatch"] is not None:
                        savingModel(al.line_match, alg_res["lineMatch"], f"lineMatch_{id_Project}_{reg.id}_{alg}.jpg")
                        createPyramid("media/" + al.line_match.name, "media/" + al.line_match.name[:-4])

                    if alg_res["warping"] is not None:
                        savingModel(al.warping, alg_res["warping"], f"warp_{id_Project}_{reg.id}_{alg}.jpg")
                        createPyramid("media/" + al.warping.name, "media/" + al.warping.name[:-4])

                        transformed_rgb = cv2.cvtColor(alg_res["warping"], cv2.COLOR_BGR2RGB)
                        ### temporal code 4-channel image
                        #img_color2[:,:,0] = img_color2[:,:,3]
                        #img_color2[:,:,1] = img_color2[:,:,3]
                        #img_color2[:,:,2] = img_color2[:,:,3]

                        ### end temporal code
                        img_color2_rgb = cv2.cvtColor(img_color2, cv2.COLOR_BGR2RGB)

                        img2_ori_stk = sitk.GetImageFromArray(transformed_rgb, isVector=True)
                        img1_stk = sitk.GetImageFromArray(img_color2_rgb, isVector=True)

                        img2_ori_stk.SetSpacing([1.0, 1.0])
                        img1_stk.SetSpacing([1.0, 1.0])

                        image_list = sitk.CheckerBoard(img2_ori_stk, img1_stk, [4, 4, 4])

                        ##convert itk to array
                        array = sitk.GetArrayFromImage(image_list)
                        array_rgb = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

                        # array_rgb = reduceImage(array_rgb)

                        savingModel(al.chessboard, array_rgb, f"chess_{id_Project}_{reg.id}_{alg}.jpg")
                        createPyramid("media/" + al.chessboard.name, "media/" + al.chessboard.name[:-4])

                        ann = AnnotationsJson.objects.filter(project=id_Project)
                        if ann and  (alg_res["homography"] is not None):

                            checkWrap = AnnotationswrapJson.objects.filter(project=project,algorithm=al.algorithm)
                            #print(checkWrap)
                            if checkWrap:
                                wrapAnn = checkWrap[0]
                            else:
                                wrapAnn = AnnotationswrapJson(project=project, annotation=ann[0].annotation, algorithm=al.algorithm)
                                wrapAnn.save()
                            homography = alg_res["homography"]
                            split = im2Name.split("/")
                            mov_filename = split[-1]

                            jsonDict = wrapAnn.annotation
                            #print("jsonDict: ", jsonDict)
                            # arrAnn = jsonDict["annotations"]
                            split = im1Name.split("/")
                            fix_filename = split[-1]

                            dictImages = [im for im in jsonDict["images"] if (im["file_name"] == mov_filename) or (im["file_name"] == fix_filename)]
                            #print("dictImages: ",dictImages)
                            id_image = dictImages[0]["id"]

                            arrAnn = [a for a in jsonDict["annotations"] if a["image_id"] == id_image]
                            newDict = copy.deepcopy(jsonDict)

                            for indxAnn, an in enumerate(arrAnn):
                                seg = an["segmentation"]
                                id_annotation = an["id"]
                                index_set = next((index for (index, d) in enumerate(jsonDict["annotations"]) if
                                                  d["id"] == id_annotation), None)
                                newseg = []
                                for indxSeg, s in enumerate(seg):
                                    #print("indxAnn: ", indxAnn, " indxSeg: ", indxSeg)
                                    #poly = np.array(s).reshape((int(len(s) / 2), 2))
                                    #print("poly: ", poly)
                                    #print("s: ", s)
                                    #dor product betwen homography and a matrix
                                    # x
                                    # y
                                    # 1
                                    #pol_tuplas = [(s[i],s[i+1]) for i in range(0, len(s), 2)]
                                    #print("area1: ", Polygon(pol_tuplas).area)
                                    matrixDot = [np.dot(homography, [[s[i]], [s[i + 1]], [1]]) for i in
                                                 range(0, len(s), 2)]
                                    newPoli = []
                                    for i in matrixDot:
                                        newPoli.append(float(i[0] / i[2]))
                                        newPoli.append(float(i[1] / i[2]))
                                    pol_tuplas2 = [(newPoli[i], newPoli[i + 1]) for i in range(0, len(newPoli), 2)]
                                    # print("area2: ", Polygon(pol_tuplas2).area)

                                    newDict["annotations"][index_set]["area"] = Polygon(pol_tuplas2).area
                                    bounds_seg = Polygon(pol_tuplas2).bounds
                                    newDict["annotations"][index_set]["bbox"] = [bounds_seg[0], bounds_seg[1],
                                                                                 bounds_seg[2] - bounds_seg[0],
                                                                                 bounds_seg[3] - bounds_seg[1]]

                                    # print("bounds_Shap: ", Polygon(pol_tuplas2).bounds)

                                    newseg.append(newPoli)

                                    # polygons.append(poly)
                                newDict["annotations"][index_set]["segmentation"] = newseg


                            index_images = next((index for (index, d) in enumerate(newDict["images"]) if
                                                 d["id"] == id_image), None)
                            # change this section for batch (now is only for one image)
                            height, width, _ = img_color2.shape
                            newDict["images"][index_images] = {"file_name": fix_filename, "height": height,
                                                               "width": width, "id": id_image}

                            # print(jsonDict["annotations"])

                            wrapAnn.annotation = newDict
                            wrapAnn.save()
                            al.annotation_wrap = wrapAnn
                            al.save()
                    res["result"].append(alg_res["succ"])


                    data = {"result": res}

    return JsonResponse(data)

#
