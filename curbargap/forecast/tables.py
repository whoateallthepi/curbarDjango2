import django_tables2 as tables
from .models import TimeSeries, Symbol
from django.utils.html import format_html
from django.conf import settings
from math import trunc

#from .utils import get_weather


class OneDecimalColumn(tables.Column):
    def render(self, value):
        return '{:0.1f}'.format(value)

class MphColumn(tables.Column):
    def render(self, value):
        whole = trunc(value)
        return str(whole) + ' mph'
        #return '{:0.0f}'.format(value)        

class ImageColumn(tables.Column):
        def render(self, value):
            #wt = get_weather(value) # revisit this weird reverse lookup
            wt = 'work inprogress'
            #breakpoint()
            return format_html(
               '<img src="{url}" height="60px", width = "60px", class = "weather_symbol" alt="{wt}" title="{wt}">',
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
    windSpeed10m = MphColumn(verbose_name = 'Wind')
    feelsLikeTemperature = OneDecimalColumn(verbose_name = 'Feel')

    symbol = ImageColumn(accessor='get_symbol',
                           verbose_name = 'Weather')
    
    screenTemperature = OneDecimalColumn(verbose_name = (u'\u00B0' + 'C')) # degrees sign
    probOfPrecipitation = tables.Column(verbose_name = '%Rain')
    

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
                  