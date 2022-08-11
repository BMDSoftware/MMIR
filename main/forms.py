from django import forms
from main.models import *

class ProjectForm(forms.Form):
    img1 = forms.FileField(label='select one file')
    img2= forms.FileField(label='select one file')
    pName = forms.CharField()
    algNum = forms.IntegerField()
