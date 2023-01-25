from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Registration_Images)
class Registration_ImagesAdmin(admin.ModelAdmin):
    search_fields = ('project',)
    list_display = ('project',)
    list_filter = ('project',)


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
    search_fields = ('Registration_Images','algorithm')
    list_display = ('name_project','name_algorithm')
    list_filter = ('Registration_Images','algorithm')

    def name_project(self, obj):
        return obj.Registration_Images.project.name
    def name_algorithm(self, obj):
        return obj.Registration_Images.project.name

@admin.register(AnnotationsJson)
class AnnotationsJsonAdmin(admin.ModelAdmin):
    search_fields = ('project', )
    list_display = ('name_project', 'id')
    list_filter = ('project', )

    def name_project(self, obj):
        return obj.project.name

@admin.register(AnnotationswrapJson)
class AnnotationswrapJsonAdmin(admin.ModelAdmin):
    search_fields = ('project', )
    list_display = ('name_project', 'id')
    list_filter = ('project', )

    def name_project(self, obj):
        return obj.project.name
