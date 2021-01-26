import django_tables2 as tables
from .models import TimeSeries, Symbol
from django.utils.html import format_html
from django.conf import settings

#from .utils import get_weather

class ImageColumn(tables.Column):
        def render(self, value):
            #wt = get_weather(value) # revisit this weird reverse lookup
            wt = 'work inprogress'
            return format_html(
               '<img src="{url}" height="60px", width = "60px", class = "weather_symbol", alt = "{wt}", title = "{wt}" >',
                url=(settings.MEDIA_URL + value),
                wt=(wt)
                )

class TimeSeriesTable(tables.Table):
    #def __init__(self,*args,**kwargs):
    #    super().__init__(*args,**kwargs)
    #    self.base_columns['wind_direction'].verbose_name = 'Rose'
    
    #date_header = 'date header'
    series_time = tables.DateTimeColumn(format ='gA')
    windDirectionFrom10m = tables.Column(verbose_name = 'From')
    windSpeed10m = tables.Column(verbose_name = 'Speed')
    feelsLikeTemperature = tables.Column(verbose_name = 'Feel')

    symbol = ImageColumn(accessor='get_symbol',
                           verbose_name = 'Weather')
    
    class Meta:
        attrs = {"class": "table"}
        model = TimeSeries
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('series_time',
                  'symbol',
                  #'significantWeatherCode', 
                  'screenTemperature',
                  'feelsLikeTemperature',
                  'probOfPrecipitation',
                  'windSpeed10m',
                  'windDirectionFrom10m',
                  'uvIndex',)
                  
        