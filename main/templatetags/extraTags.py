from django import template
from main.models import *

register = template.Library()

@register.filter(name='getFirstAlg')
def getFirstAlg(project_id):
    algorithms = Results.objects.filter(project=project_id)

    return algorithms[0].algorithm.id