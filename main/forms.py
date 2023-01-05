from django import forms
from main.models import *

class ProjectForm(forms.Form):
    img1 = forms.FileField()
    img2= forms.FileField()
    pName = forms.CharField()
    algNum = forms.IntegerField()
