from django.db import models
from django.utils.timezone import now

# Create your models here.
class Movie(models.Model):
    
    title = models.CharField(verbose_name="titre", max_length=256, blank=False, default="")
    url = models.CharField(max_length=256, default="")
    picture_url = models.CharField(max_length=256, default="")
    synopsis = models.CharField(max_length=1500, default="")
    predicted_affluence = models.PositiveIntegerField(verbose_name="Affluence prédite", default=0)
    date = models.DateField(default=now)