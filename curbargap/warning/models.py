#from django.db import models
from django.contrib.postgres.fields import ArrayField
#from djgeojson.fields import MultiPolygonField
from django.contrib.gis.db import models 
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.db import transaction
from django.conf import settings

from django.db.models import DEFERRED

from django.utils import timezone
    
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
    
    # following saves previous values when updating
    @classmethod
    def from_db(cls, db, field_names, values):
        # Default implementation of from_db() (subject to change and could
        # be replaced with super()).
        if len(values) != len(cls._meta.concrete_fields):
            values = list(values)
            values.reverse()
            values = [
                values.pop() if f.attname in field_names else DEFERRED
                for f in cls._meta.concrete_fields
            ]
        instance = cls(*values)
        instance._state.adding = False
        instance._state.db = db
        # customization to store the original field values on the instance
        instance._loaded_values = dict(
            zip(field_names, (value for value in values if value is not DEFERRED))
        )
        return instance
    
    
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
        THUNDERSTORM = 1, 'thunderstorm'
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
        CANCELLED = 2, 'cancelled' 
        OTHER = 3, 'unknown'    
    
    warningId = models.UUIDField('Warning ID',primary_key=True)
    service =  models.ForeignKey(Service,on_delete=models.CASCADE)
    issuedDate = models.DateTimeField('Warning Time')
    notifiedDate = models.DateTimeField('Notified Time', blank=True, null=True)
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

        
    def save(self, **kwargs):
        #
        from warning.classes import Notification # avoid circular import...
        def send_notify_message(warning_id):
            nn = Notification(warning_id,settings.SMS_SERVER,settings.SMS_PORT)
            nn.send()
        
        # Check how the current values differ from ._loaded_values. 
        #
        if not self._state.adding:
            # preserve the notified date on updates to avoid duplciates
            #            
            self.notifiedDate = self._loaded_values['notifiedDate']

            print ('Warning update detected - preserving notified date = {}for warningId {}'.
                   format(self.notifiedDate, self.warningId))
        # logic not quite rigth .....
        super().save(**kwargs)
        
        # save notified date
        self._original_notifiedDate = self.notifiedDate

        # decide if we are going to notify, ie never been notified or
        # modified since lat notification
        notify = False
        if  (not self._original_notifiedDate) or ((
            self.warningStatus == Warning.Status.ISSUED) and (
            self._original_notifiedDate < self.modifiedDate)):
            notify = True
            # notification will happen so update notifiedDate
            self.notifiedDate = timezone.now()

        print("saving warning...")
        super(Warning, self).save(**kwargs)
        
        if notify:
            print("Sending notification(s) for warning id {}".format(self.warningId))
            transaction.on_commit(lambda: send_notify_message(self.warningId))
        else: 
            print("Skipping  notification {}, status : {} - appears to be a repeat".
                  format(self.warningId, self.warningStatus))   
    
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
                return 'thunderstorm'
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
    
class Location (models.Model):
    name = models.CharField('location', max_length=50, unique=True, db_index=True)
    area = models.MultiPolygonField('geometry',blank=True, null=True)

    # force upper case
    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name    
    
class Device (models.Model):
    
    class DeviceType (models.IntegerChoices):
        SMS = 0, 'sms'

    type = models.IntegerField('device type', choices = DeviceType.choices)
    phoneNumber = PhoneNumberField()

    class Meta:
        unique_together = ('type', 'phoneNumber',)

    def __str__(self):
        return str(self.phoneNumber)

class Subscription (models.Model):

    class SubscriptionType (models.IntegerChoices):
        WEATHER = 0, 'weather',
        FROST = 1, 'frost',
        FLOOD = 2, 'flood'
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    type = models.IntegerField('subscription type', choices = SubscriptionType.choices)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('device', 'type','location',)