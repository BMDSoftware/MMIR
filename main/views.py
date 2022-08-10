from django.shortcuts import render
from main.models import *

# Create your views here.
def home(request):
    dtable = Projects.objects.all().order_by('name')
    alg = Algorithms.objects.all().order_by('name')
    context = {'dtable':dtable,
               'alg': alg}


    return render(request, 'index.html', context)