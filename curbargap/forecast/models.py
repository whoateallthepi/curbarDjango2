from django.db import models, connection
from django.urls import reverse

# Create your models here.

class Forecast(models.Model):
    latitude = models.DecimalField('latitude', max_digits=10, decimal_places=7)
    longitude = models.DecimalField('longitude', max_digits=10, decimal_places=7)
    name = models.CharField('location name', max_length=60)
    forecast_date = models.DateTimeField('date')
    distance = models.DecimalField('distance from request point', max_digits=9, decimal_places=4)

    def __str__(self):
        return ( self.forecast_date.strftime('%Y-%m-%d %H:%M %z') + ' : ' + self.name )

    def get_absolute_url(self):
        return reverse('forecast:forecast_detail',
                       args=[str(self.id)] )
    class Meta:
        ordering = ['-forecast_date']                   

class Symbol (models.Model):
   weather_code = models.IntegerField('weather_code', unique=True)
   symbol_image = models.ImageField(upload_to='symbols/',
                                     blank=True)
   weather_type = models.CharField('Weather', max_length=30)  

class TimeSeries(models.Model):
    forecast = models.ForeignKey(Forecast, 
               on_delete = models.CASCADE)
    feelsLikeTemperature = models.DecimalField('feels like', max_digits=4, decimal_places=2)
    max10mWindGust = models.DecimalField('max. 10m wind gust', 
                                          max_digits=10, decimal_places=6,blank=True, null=True)
    maxScreenAirTemp = models.DecimalField('maximum temperature', 
                                            max_digits=9, decimal_places=6,blank=True,null=True)
    minScreenAirTemp = models.DecimalField( 'minimum temperature', 
                                             max_digits=9, decimal_places=6, blank=True, null=True)
    mslp = models.DecimalField('pressure',max_digits=7,decimal_places=2)
    precipitationRate = models.DecimalField('Rainfall rate', max_digits=5, decimal_places=2)
    probOfPrecipitation = models.IntegerField('Chance of rain')
    screenDewPointTemperature = models.DecimalField('dew point', max_digits=5, decimal_places=2)
    screenRelativeHumidity = models.DecimalField('Humidity', max_digits=5, decimal_places=2)
    screenTemperature = models.DecimalField('temperature', max_digits=5, decimal_places=2)
    significantWeatherCode = models.IntegerField('weather code', blank=True, null=True)     
    
    def get_symbol(self):
      with connection.cursor() as cursor:
        cursor.execute("SELECT symbol_image from forecast_symbol where weather_code = %s",
                       [self.significantWeatherCode])
        row = cursor.fetchone()
      #breakpoint()
      return row [0]

    series_time = models.DateTimeField('time')
    totalPrecipAmount = models.DecimalField('total precipitation', max_digits=5, decimal_places=2)
    totalSnowAmount = models.DecimalField('snow amount', max_digits=5, decimal_places=2)
    uvIndex = models.IntegerField('UV')
    visibility = models.IntegerField('visibility')
    windDirectionFrom10m = models.IntegerField('wind direction')
    windGustSpeed10m = models.DecimalField('wind gust', max_digits=5, decimal_places=2)
    windSpeed10m = models.DecimalField('wind speed', max_digits=5, decimal_places=2)
    
    class Meta:
        ordering = ['series_time'] 

