# -*- coding: utf-8 -*-
from django.urls import path, re_path
from . import views

app_name = 'urbanSound'

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    #re_path(r'^about/$', views.historial, name =  'about'),

]