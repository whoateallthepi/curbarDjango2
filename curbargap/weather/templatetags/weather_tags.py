from django import template
from ..models import Reading
from blog.models import Post


from django.conf import settings

from ..classes import LatestForecast, LatestReading

register = template.Library()

@register.inclusion_tag('weather/reading/current_weather.html')
def show_latest_reading(station=settings.DEFAULT_STATION):
    current_weather =  Reading.objects.filter(station__exact=station).latest('reading_time')
    return { 'current_weather' : current_weather }

@register.inclusion_tag('weather/reading/temperature.html')
def temperature_now (station=settings.DEFAULT_STATION):
    lr=LatestReading(station=station) # note stations are different for readings

    return { 'latest_reading' : lr.reading,
             
    }