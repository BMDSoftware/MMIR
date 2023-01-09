from django import template
from main.models import *
import math

register = template.Library()

@register.filter(name='getFirstAlg')
def getFirstAlg(project_id):
    algorithms = Results.objects.filter(Registration_Images__project=project_id)

    if algorithms:
        return algorithms[0].algorithm.id
    else:
        return "None"

@register.filter(name='getFirstFiles')
def getFirstFiles(project_id):
    res = Registration_Images.objects.filter(project=project_id)

    if res:
        return res[0].id
    else:
        return "None"

@register.filter(name='getArrValue')
def getArrValue(arr,index):
    return arr[index]

@register.filter(name='getXorY')
def getXorY(arr,eval):
    if eval == "x":
        return arr[0]
    else:
        return arr[1]

@register.filter(name='getMod')
def getMod(val1,val2):
    #number_of_points = len(arrayPoints)
    #factor = math.ceil(number_of_points / 100)
    res =  val1 % val2
    if res == 0:
        return True
    else:
        return False
