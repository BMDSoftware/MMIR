# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views

app_name = 'main'

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^saveNP/$', views.saveNP, name='saveNP'),
    re_path(r'^viewer/$', views.viewer, name='viewer'),

    #re_path(r'^about/$', views.historial, name =  'about'),

]