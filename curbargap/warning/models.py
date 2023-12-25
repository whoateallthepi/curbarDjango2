from django.db import models
from django.contrib.postgres.fields import ArrayField
from djgeojson.fields import MultiPolygonField

from django.utils import timezone
from django.urls import reverse

# Create your models here.
class Service(models.Model):
    name = models.CharField('Service Name', max_length=10)
    lastUpdate = models.DateTimeField('Last update Time', blank=True, null=True)
#
class WeatherType (models.IntegerChoices):
    RAIN = 0, 'rain'
    THUNDERSTORMS = 1, 'thunderstorms'
    WIND = 2, 'wind'
    SNOW = 3, 'snow'
    LIGHTNING = 4, 'lightning'
    ICE = 5, 'ice'
    EXTREME_HEAT = 6, 'extreme heat'
    FOG = 7, 'fog'

class WarningLevel(models.IntegerChoices):
    YELLOW = 0, 'yellow'   
    AMBER = 1, 'amber'
    RED = 2, 'red'

class Likelihood(models.IntegerChoices):
    UNLIKELY = 1, 'unlikely'
    LOW = 2, 'low'
    MEDIUM = 3, 'medium'
    VERY_LIKELY = 4, 'very likely'

class Impact(models.IntegerChoices): 
    VERY_LOW = 1, 'very low'
    LOW = 2, 'low'
    MEDIUM = 3, 'medium'
    HIGH = 4, 'high' 

class Status(models.IntegerChoices):
    EXPIRED = 0, 'expired'
    ISSUED = 1, 'issued'     

class Warning(models.Model):
    warningId = models.UUIDField('Warning ID',primary_key=True)
    service =  models.ForeignKey(Service,on_delete=models.CASCADE)
    issuedDate = models.DateTimeField('Reading Time')
    weatherType = ArrayField(models.IntegerField('type',
                                      choices=WeatherType.choices))
    warningLikelihood = models.IntegerField('Likelihood',
                                            choices=Likelihood.choices)
    warningLevel = models.IntegerField('Level',
                                         choices=WarningLevel.choices)
    warningStatus = models.IntegerField('Status',
                                        choices=Status.choices)
    warningHeadline = models.CharField('Headline',max_length=80)
    whatToExpect = models.CharField('What to expect', max_length=1000)
    modifiedDate = models.DateTimeField('Modified date')
    validFromDate = models.DateTimeField('Valid from')
    validToDate = models.DateTimeField('Valid to')
    affectedAreas = models.JSONField()
    warningImpact =  models.IntegerField('Impact',
                                         choices=Impact.choices) 
    geometry = MultiPolygonField('Geometry')