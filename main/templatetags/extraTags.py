from django import template
from main.models import *

register = template.Library()

@register.filter(name='getFirstAlg')
def getFirstAlg(project_id):
    algorithms = Results.objects.filter(project=project_id)

    return algorithms[0].algorithm.id

@register.filter(name='getArrValue')
def getArrValue(arr,index):
    return arr[index]

@register.filter(name='getXorY')
def getXorY(arr,eval):
    if eval == "x":
        return arr[0]
    else:
        return arr[1]