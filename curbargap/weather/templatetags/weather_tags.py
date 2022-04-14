from django import template
from ..models import Reading
from blog.models import Post


from django.conf import settings

from ..classes import LatestForecast, LatestReading

register = template.Library()

@register.inclusion_tag('weather/reading/current_weather.html')
def show_latest_reading(station=settings.DEFAULT_STATION):
    #breakpoint()
    return { 'current_weather' : Reading.objects.filter(station__exact=station).latest('reading_time') }



@register.inclusion_tag('weather/reading/temperature.html')
def temperature_now (station=3):
    lr=LatestReading() # note stations are different for readings

    return { 'latest_reading' : lr.reading,
             
    }