from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Projects)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
    list_filter = ('name',)

@admin.register(Algorithms)
class AlgorithmAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
    list_filter = ('name',)

@admin.register(Results)
class ResultAdmin(admin.ModelAdmin):
    search_fields = ('project','algorithm')
    list_display = ('name_project','name_algorithm')
    list_filter = ('project','algorithm')

    def name_project(self, obj):
        return obj.project.name
    def name_algorithm(self, obj):
        return obj.algorithm.name



@admin.register(Metrics)
class MetricsAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name','value')
    list_filter = ('name',)