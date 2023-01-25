# -*- coding: utf-8 -*-
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'main'

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^saveNP/$', views.saveNP, name='saveNP'),
    re_path(r'^viewer/(?P<id_Project>[0-9]\d*)/(?P<id_viewer>[0-9]\d*)/(?P<id_reg_img>[0-9]\d*)/(?P<id_alg>.+$)', views.viewer, name='viewer'),
    path('viewer/<int:id_Project>', views.viewer, name='viewer'),
    path('downloadFiles/<int:id_Project>', views.downloadFiles, name='downloadFiles'),
    path('runAlg/', views.runAlg, name='runAlg'),
    path('dynamicChessboard/', views.dynamicChessboard, name='dynamicChessboard'),
    path('deleteProject/<int:id_Project>', views.deleteProject, name='deleteProject'),

    #re_path(r'^about/$', views.historial, name =  'about'),

]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)