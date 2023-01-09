from django.db import models
from main.storage import OverwriteStorage
from jsonfield import JSONField


# Create your models here.

def image_fix_path(instance, filename):
    return  'img/fixed/{0}/{1}'.format(instance.project.id, filename)

def image_mov_path(instance, filename):
    return  'img/moving/{0}/{1}'.format(instance.project.id, filename)

def results_warp(instance, filename):
    return  'img/results/warp/{0}/{1}'.format(instance.Registration_Images.project.id, filename)

def results_feature_mov(instance, filename):
    return  'img/results/feature_mov/{0}/{1}'.format(instance.Registration_Images.project.id, filename)

def results_feature_fix(instance, filename):
    return  'img/results/feature_fix/{0}/{1}'.format(instance.Registration_Images.project.id, filename)

def results_line_match(instance, filename):
    return  'img/results/line_match/{0}/{1}'.format(instance.Registration_Images.project.id, filename)

def results_chess(instance, filename):
    return  'img/results/chess/{0}/{1}'.format(instance.Registration_Images.project.id, filename)

class Projects(models.Model):
    name = models.CharField(max_length=255, null=True)
    #image1 = models.ImageField(upload_to='img/fixed/')
    #image2 = models.ImageField(upload_to='img/moving/')

    def __unicode__(self):
        return unicode(self.name)

class Registration_Images(models.Model):
    project = models.ForeignKey('Projects', on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to=image_fix_path)
    image2 = models.ImageField(upload_to=image_mov_path)
    def __unicode__(self):
        return unicode(self.project.name)


class Algorithms(models.Model):
    name = models.CharField(max_length=255, null=True)
    def __unicode__(self):
        return unicode(self.name)

class Results(models.Model):
    warping = models.ImageField(max_length=255, storage=OverwriteStorage(),upload_to=results_warp, blank=True)
    features_mov = models.ImageField(max_length=255,storage=OverwriteStorage(),upload_to= results_feature_mov, blank=True)
    features_fix = models.ImageField(max_length=255,storage=OverwriteStorage(),upload_to=results_feature_fix, blank=True)
    line_match = models.ImageField(max_length=255,storage=OverwriteStorage(), upload_to=results_line_match , blank=True)
    chessboard = models.ImageField(max_length=255,storage=OverwriteStorage(), upload_to=results_chess, blank=True)
    x_chessboard = models.PositiveSmallIntegerField(default=4)
    y_chessboard = models.PositiveSmallIntegerField(default=4)
    annotation_wrap = JSONField(default={})

    algorithm = models.ForeignKey('Algorithms', on_delete=models.CASCADE)
    Registration_Images = models.ForeignKey('Registration_Images', on_delete=models.CASCADE, null=True)

    def __unicode__(self):
        return unicode(self.Registration_Images.project.name +  " - " + self.algorithm.name )


class AnnotationsJson(models.Model):
  annotation = JSONField(default ={})
  project = models.ForeignKey('Projects', on_delete=models.CASCADE)

  def __unicode__(self):
      return unicode(self.project.name + " - " + self.id)


