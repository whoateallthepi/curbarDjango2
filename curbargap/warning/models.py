#from django.db import models
from django.contrib.postgres.fields import ArrayField
#from djgeojson.fields import MultiPolygonField
from django.contrib.gis.db import models 
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.urls import reverse

import json

# Create your models here.
class Service(models.Model):
    name = models.CharField('Service Name', max_length=10)
    lastUpdate = models.DateTimeField('Last update Time', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('warning:service_detail',
                       args=[str(self.id)] )
    
    def __str__(self):
        return str(self.id)
#

class Warning(models.Model):
    
    def display_weatherType (self):
        if self.weatherType == 0:
            return 'rain'
        if self.weatherType == 1:
            return 'thunderstorms'
        if self.weatherType == 2:
            return 'wind'
        if self.weatherType == 3:
            return 'snow'
        if self.weatherType == 4:
            return 'lightning'
        if self.weatherType == 5:
            return 'ice'
        if self.weatherType == 6:
            return 'extreme heat'
        if self.weatherType == 7:
            return 'fog'
        else:
            return 'unknown'

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
    warningHeadline = models.CharField('Headline',max_length=200)
    whatToExpect = models.CharField('What to expect', max_length=1000)
    modifiedDate = models.DateTimeField('Modified date')
    validFromDate = models.DateTimeField('Valid from')
    validToDate = models.DateTimeField('Valid to')
    affectedAreas = models.JSONField()
    warningImpact =  models.IntegerField('Impact',
                                         choices=Impact.choices) 
    geometry = models.MultiPolygonField('Geometry',blank=True, null=True)

    def get_absolute_url(self):
        return reverse('warning:warning_detail',
                       args=[str(self.warningId)] )
    
    def __str__(self):
        return str(self.warningId)
    
    def get_geojson (self):
        # Get a JSON version of the MULTIPOLYGON warning area and put a wrapper
        # on it to conform to GEOJson standard
        #
        gg = GEOSGeometry(self.geometry) 
        gj = '{ "type": "Feature", "geometry" : '  + gg.json + ', "properties": { "name": "warning area" }}'
        return gj
     
    def display_weatherType (self):
        def decode (wt):
            if wt == 0:
                return 'rain'
            if wt == 1:
                return 'thunderstorms'
            if wt == 2:
                return 'wind'
            if wt == 3:
                return 'snow'
            if wt == 4:
                return 'lightning'
            if wt == 5:
                return 'ice'
            if wt == 6:
                return 'extreme heat'
            if wt == 7:
                return 'fog'
            else:
                return 'unknown'
        decoded = []
        
        for wt in self.weatherType:
            decoded.append(decode(wt))   
        
        return decoded 

    def display_regions(self):
        # creates a list of affected regions
        region_list = []
        regions = json.loads(self.affectedAreas)
        for region in regions:
            region_list.append(region['regionName'])

        return region_list