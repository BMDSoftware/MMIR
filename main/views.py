from django.shortcuts import render
from main.models import *
from main.forms import *
from django.http import JsonResponse
import json

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


def viewer(request,id_Project):
    project = Projects.objects.get(id=id_Project)
    img1 = project.image1
    img2 = project.image2

    context= {"fixImg": img1,"movImag": img2}



    return render(request, 'viewer.html', context)