from django import template
from ..models import Reading
from ..models import AstronomicalData, Station
from blog.models import Post
from datetime import datetime, timezone
#from django.utils import timezone


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

    return { 'latest_reading' : lr.reading,}

@register.inclusion_tag('weather/astronomicaldata/today.html')
def show_todays_astrodata(station=settings.DEFAULT_STATION):
    
    today = datetime.now(timezone.utc).date()

    ss = Station.objects.get(pk=settings.DEFAULT_STATION)
    
    astro, created = AstronomicalData.objects.get_or_create(station=ss, date = today)
    
    return { 'astro_data' : astro,}    