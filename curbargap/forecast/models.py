from django.db import models, connection
from django.urls import reverse

# Create your models here.

class Forecast(models.Model):
    THREE_HOURLY = 3
    HOURLY = 1
    TYPES_OF_FORECAST = [
       (THREE_HOURLY, 'three-hourly'),
       (HOURLY, 'hourly')
    ]
    
    type = models.IntegerField('type', choices=TYPES_OF_FORECAST, default=HOURLY)
    latitude = models.DecimalField('latitude', max_digits=10, decimal_places=7)
    longitude = models.DecimalField('longitude', max_digits=10, decimal_places=7)
    name = models.CharField('location name', max_length=60)
    forecast_date = models.DateTimeField('date')
    distance = models.DecimalField('distance from request point', max_digits=9, decimal_places=4)

    def __str__(self):
        return ( self.forecast_date.strftime('%Y-%m-%d %H:%M %z') +
                ' : Type: ' + str(self.type ) + ' for: ' + self.name )

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
    feelsLikeTemperature = models.DecimalField('feels like', max_digits=4, decimal_places=2,blank=True, null=True)
    max10mWindGust = models.DecimalField('max. 10m wind gust', 
                                          max_digits=10, decimal_places=6,blank=True, null=True)
    maxScreenAirTemp = models.DecimalField('maximum temperature', 
                                            max_digits=9, decimal_places=6,blank=True,null=True)
    minScreenAirTemp = models.DecimalField( 'minimum temperature', 
                                             max_digits=9, decimal_places=6, blank=True, null=True)
    mslp = models.DecimalField('pressure',max_digits=7,decimal_places=2,blank=True, null=True)
    precipitationRate = models.DecimalField('Rainfall rate', max_digits=5, decimal_places=2,blank=True, null=True)
    probOfPrecipitation = models.IntegerField('Chance of rain', blank=True, null=True)
    screenDewPointTemperature = models.DecimalField('dew point', max_digits=5, decimal_places=2,blank=True, null=True)
    screenRelativeHumidity = models.DecimalField('Humidity', max_digits=5, decimal_places=2,blank=True, null=True)
    screenTemperature = models.DecimalField('temperature', max_digits=5, decimal_places=2,blank=True, null=True)
    significantWeatherCode = models.IntegerField('weather code', blank=True, null=True)     
    
    def get_symbol(self):
      with connection.cursor() as cursor:
        cursor.execute("SELECT symbol_image from forecast_symbol where weather_code = %s",
                       [self.significantWeatherCode])
        row = cursor.fetchone()
      #breakpoint()
      return row [0]

    series_time = models.DateTimeField('time')
    totalPrecipAmount = models.DecimalField('total precipitation', max_digits=5, decimal_places=2,blank=True, null=True)
    totalSnowAmount = models.DecimalField('snow amount', max_digits=5, decimal_places=2,blank=True, null=True)
    uvIndex = models.IntegerField('UV',blank=True, null=True)
    visibility = models.IntegerField('visibility',blank=True, null=True)
    windDirectionFrom10m = models.IntegerField('wind direction',blank=True, null=True)

    def get_arrow(self):

      def get_rose(degrees):
       #Utility to convert degrees to a human direction
       # At the moment I only have a limited arrow set
       sectors = ["N",
                   #"NNE",
                   "NE",
                   #"ENE",
                   "E",
                   #"ESE",
                   "SE",
                   #"SSE",
                   "S",
                   #"SSW",
                   "SW",
                   #"WSW",
                   "W",
                   #"WNW",
                   "NW",
                   #"NNW",
                   "N"
                 ]
       big_degrees = (360 + 22.5) + degrees
       sector = int(big_degrees/45)
       #force into range 0-7, with 0 = N 
       if sector >= 8:
         sector -= 8
       return sectors[sector]
       # end of get_rose
      
      rose = get_rose(self.windDirectionFrom10m) # produces 'NW', 'SE' etc
      with connection.cursor() as cursor:
        cursor.execute("SELECT arrow_image from forecast_arrow where direction_from = %s", [rose])
        row = cursor.fetchone()
      #breakpoint()
      return row [0]

    windGustSpeed10m = models.DecimalField('wind gust', max_digits=5, decimal_places=2,blank=True, null=True)
    windSpeed10m = models.DecimalField('wind speed', max_digits=5, decimal_places=2,blank=True, null=True)
    probOfSnow=models.IntegerField('chance of snow',blank=True, null=True)
    probOfHeavySnow=models.IntegerField('chance of heavy snow',blank=True, null=True)
    probOfRain=models.IntegerField('chance of rain',blank=True, null=True)
    probOfHeavyRain=models.IntegerField('chance of heavy rain',blank=True, null=True)
    probOfHail=models.IntegerField('chance of hail',blank=True, null=True)
    probOfSferics=models.IntegerField('chance of lightning (sferics)',blank=True, null=True)

    class Meta:
        ordering = ['series_time'] 

class Arrow (models.Model):
   direction_from = models.CharField('wind from', unique=True,max_length=3)
   arrow_image = models.ImageField(upload_to='arrows/',
                                     blank=True)
   def __str__(self):
        return self.direction_from                                
