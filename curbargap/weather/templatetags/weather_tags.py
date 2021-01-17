from django import template
from ..models import Reading
from blog.models import Post

from ..classes import LatestForecast, LatestReading

register = template.Library()

@register.inclusion_tag('weather/reading/current_weather.html')
def show_latest_reading(station=3):
    #breakpoint()
    return { 'current_weather' : Reading.objects.filter(station__exact=station).latest('reading_time') }

@register.inclusion_tag('weather/forecast/latest.html')
def show_latest_forecast(station=351418):
    lf=LatestForecast(station)
    #breakpoint()
    lr=LatestReading() # note stations are different for readings

    return { 'current_symbol' : lf.symbol,
             'weather_type'   : lf.weather_type,
             'latest_reading' : lr.reading,
             
    }

@register.inclusion_tag('weather/reading/temperature.html')
def temperature_now (station=3):
    lr=LatestReading() # note stations are different for readings

    return { 'latest_reading' : lr.reading,
             
    }