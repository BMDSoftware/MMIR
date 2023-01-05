from django.db import models
from main.storage import OverwriteStorage
from jsonfield import JSONField


# Create your models here.

def image_fix_path(instance, filename):
    return  'img/fixed/{0}/{1}'.format(instance.project.id, filename)

def image_mov_path(instance, filename):
    return  'img/moving/{0}/{1}'.format(instance.project.id, filename)

class Projects(models.Model):
    name = models.CharField(max_length=255, null=True)
    #image1 = models.ImageField(upload_to='img/fixed/')
    #image2 = models.ImageField(upload_to='img/moving/')

    def __unicode__(self):
        return unicode(self.name)

class Fix_Images(models.Model):
    project = models.ForeignKey('Projects', on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to=image_fix_path)

class mov_Images(models.Model):
    project = models.ForeignKey('Projects', on_delete=models.CASCADE)
    image2 = models.ImageField(upload_to=image_mov_path)

class Algorithms(models.Model):
    name = models.CharField(max_length=255, null=True)
    def __unicode__(self):
        return unicode(self.name)

class Results(models.Model):
    warping = models.ImageField(max_length=255, storage=OverwriteStorage(),upload_to='img/results/warp/', blank=True)
    features_mov = models.ImageField(max_length=255,storage=OverwriteStorage(),upload_to='img/results/f_mov/', blank=True)
    features_fix = models.ImageField(max_length=255,storage=OverwriteStorage(),upload_to='img/results/f_fix/', blank=True)
    line_match = models.ImageField(max_length=255,storage=OverwriteStorage(), upload_to='img/results/l_match/', blank=True)
    chessboard = models.ImageField(max_length=255,storage=OverwriteStorage(), upload_to='img/results/chess/', blank=True)
    x_chessboard = models.PositiveSmallIntegerField(default=4)
    y_chessboard = models.PositiveSmallIntegerField(default=4)
    annotation_wrap = JSONField(default={})

    algorithm = models.ForeignKey('Algorithms', on_delete=models.CASCADE)
    project = models.ForeignKey('Projects', on_delete=models.CASCADE)

    def __unicode__(self):
        return unicode(self.project.name +  " - " + self.algorithm.name )


class AnnotationsJson(models.Model):
  annotation = JSONField(default ={})
  project = models.ForeignKey('Projects', on_delete=models.CASCADE)

  def __unicode__(self):
      return unicode(self.project.name + " - " + self.id)


