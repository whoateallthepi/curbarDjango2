from django.db import models, connection
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse


#import time
#import datetime

# Create your models here.
# Weather Station
class Station(models.Model):
   name = models.CharField('Station Name', max_length=20)
   latitude = models.DecimalField('Station Latitude', max_digits=9, decimal_places=6)
   longitude = models.DecimalField('Station Longitude', max_digits=9, decimal_places=6)
   altitude = models.IntegerField('Station Altitude')
   type = models.CharField('Station Type', max_length=3)
   RFid = models.CharField('Station RFid', max_length=2, blank=True, null=True)
   phone = models.IntegerField('Station Phone', blank=True, null=True)

   def __str__(self):
        return self.name

   def get_absolute_url(self):
       return reverse ('weather:station_detail',
                       args=[self.id])


#Readings
class Reading(models.Model):
   reading_time = models.DateTimeField('Reading Time')
   station = models.ForeignKey(Station,on_delete=models.CASCADE)
   wind_dir = models.IntegerField('Wind Direction', validators=[MaxValueValidator(360), MinValueValidator(0)])
   wind_speed = models.DecimalField('Wind Speed', max_digits=4, decimal_places=1)
   wind_gust = models.DecimalField('Wind Gust', max_digits=4, decimal_places=1)
   wind_gust_dir = models.IntegerField('Wind Direction', validators=[MaxValueValidator(360), MinValueValidator(0)])
   wind_speed_avg2m = models.DecimalField('Wind Speed 2m Average', max_digits=4, decimal_places=1)
   wind_dir_avg2m = models.IntegerField('Wind Direction 2m Average', validators=[MaxValueValidator(360), MinValueValidator(0)], default=0)
   wind_gust_10m = models.DecimalField('Wind Gust 10 minutes', max_digits=4, decimal_places=1)
   wind_gust_dir_10m = models.IntegerField('Wind Gust Direction 10m', validators=[MaxValueValidator(360), MinValueValidator(0)])
   humidity = models.DecimalField('Relative Humidity', max_digits=4, decimal_places=1, blank=True, null=True)
   temperature = models.DecimalField('Temperature Centigrade', max_digits=3, decimal_places=1)
   rain_1h = models.DecimalField('Rain Past Hour', max_digits=6, decimal_places=2, blank=True, null=True)
   rain_today = models.DecimalField('Rain Today', max_digits=6, decimal_places=2, blank=True, null=True)
   rain_since_last = models.DecimalField('Rain Since Last Reading', max_digits=6, decimal_places=2, blank=True, null=True)
   bar_uncorrected = models.FloatField('Uncorrected pressure')
   bar_corrected =  models.DecimalField('Barometer (corrected)', max_digits=5, decimal_places=1)
   battery = battery= models.DecimalField('Battery', max_digits=4, decimal_places=2, default=0, blank=True, null=True)
   light = models.DecimalField('Battery', max_digits=4, decimal_places=2, default=0, blank=True, null=True)
   
   def get_absolute_url(self):
       return reverse ('weather:reading_detail',
                       args=[self.id])

   
   def summary (self): 
      def rose(degrees):
      # Utility to convert degrees to a human direction - probably needs to be elsewhere
         quadrants = ["N",
                     "NNE",
                     "NE",
                     "ENE",
                     "E",
                     "ESE",
                     "SE",
                     "SSE",
                     "S",
                      "SSW",
                      "SW",
                      "WSW",
                      "W",
                      "WNW",
                      "NW",
                      "NNW",
                     "N"
                   ]

         big_degrees = 371.25  + degrees
         quadrant = int(big_degrees/22.5)

         #force into range 0-15, with 0 = N 
         if quadrant >= 16:
           quadrant -= 16

         return quadrants[quadrant]
      # end of rose   
      
      if self.wind_speed > 0:
         wind_rose = rose(self.wind_dir)
      else:
         wind_rose = 'Calm'
      
      return (' Weather at ' + self.reading_time.strftime("%H:%M:%S on %d %b %Y") +       
               ': Temp:{t:-0.1f}C'.format(t=self.temperature) +
               ', RH:{hd:0.0f}%'.format(hd=self.humidity) + 
               ', Wind:{wd:0.0f}km/h'.format(wd=self.wind_speed)+ 
               ' from ' + wind_rose +
               ', Bar:{p:0.0f}mb'.format(p=self.bar_corrected) +
               ', Rain today:{rt:0.1f}mm'.format(rt=self.rain_today) +
               ', Rain last hr:{rh:0.1f}mm'.format(rh=self.rain_1h) 
      ) 
# the following are for weather forecasts via Met Office DataPoint
# 

class Symbol (models.Model):
   symbol_key = models.IntegerField('symbol key', unique=True)
   symbol_image = models.ImageField(upload_to='symbols/',
                                     blank=True)
   weather_type = models.CharField('Weather', max_length=30)                                  

class Forecast(models.Model):
   forecast_time = models.DateTimeField('Reading Time')
   location = models.IntegerField('Location number')
   name = models.CharField('Station Name', max_length=30)

class Day (models.Model):
   forecast = models.ForeignKey(Forecast, on_delete=models.CASCADE, related_name='days')
   date = models.DateTimeField('Forecast day')
class Timestep (models.Model):
   day = models.ForeignKey(Day,  on_delete=models.CASCADE, related_name='timesteps')
   step_time = models.DateTimeField('Time')
   #dew_point = models.DecimalField('Dew Point', max_digits=4, decimal_places=1, null=True, blank=True)
   feels_like_temperature = models.IntegerField('Feels like')
   humidity = models.IntegerField('Humidity')
   name = models.IntegerField('Timestep name')
   precipitation = models.IntegerField('%Rain')
   temperature = models.IntegerField('°C')
   uv = models.IntegerField('UV')
   visibility = models.CharField('Visibility', max_length=2)
   #weather = models.IntegerField('Symbol')
   weather = models.ForeignKey(Symbol,
                               to_field = 'symbol_key', 
                               on_delete=models.DO_NOTHING,
                               related_name='symbol')
   weather = models.IntegerField('Symbol') 
   wind_direction = models.CharField('Rose', max_length=3)
   wind_gust = models.IntegerField('Gust') # mph
   wind_speed = models.IntegerField('Wind Speed') #mph
   
   def get_symbol(self):
      with connection.cursor() as cursor:
        cursor.execute("SELECT symbol_image from weather_symbol where symbol_key = %s", [self.weather])
        row = cursor.fetchone()
        #breakpoint()
      
      #breakpoint()
      return row [0]

class Image(models.Model):
   title = models.CharField(max_length=200)
   slug = models.SlugField(max_length=100,
                           blank = True)
   image=models.ImageField(upload_to='images/%Y/%m')
   description = models.TextField(blank=True)
   created = models.DateField(auto_now_add=True)

   def __str__(self):
      return self.title

  
   

