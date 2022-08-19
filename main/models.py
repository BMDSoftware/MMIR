from django.db import models

# Create your models here.


class Projects(models.Model):
    name = models.CharField(max_length=255, null=True)
    image1 = models.ImageField(upload_to='img/fixed/')
    image2 = models.ImageField(upload_to='img/moving/')

    def __unicode__(self):
        return unicode(self.name)

class Algorithms(models.Model):
    name = models.CharField(max_length=255, null=True)
    def __unicode__(self):
        return unicode(self.name)

class Results(models.Model):
    warping = models.ImageField(upload_to='img/results/warp/', blank=True)
    features_mov = models.ImageField(upload_to='img/results/f_mov/', blank=True)
    features_fix = models.ImageField(upload_to='img/results/f_fix/', blank=True)
    line_match = models.ImageField(upload_to='img/results/l_match/', blank=True)

    algorithm = models.ForeignKey('Algorithms', on_delete=models.CASCADE)
    project = models.ForeignKey('Projects', on_delete=models.CASCADE)

    def __unicode__(self):
        return unicode(self.project.name +  " - " + self.algorithm.name )


class Metrics(models.Model):
    name = models.CharField(max_length=255,null=True)
    value = models.DecimalField(max_digits=6, decimal_places=3,null=True)
    results = models.ForeignKey('Results', on_delete=models.CASCADE)

    def __unicode__(self):
        return unicode(self.name)