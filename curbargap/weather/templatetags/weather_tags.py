from django import template
from ..models import Reading

register = template.Library()

@register.inclusion_tag('weather/reading/current_weather.html')
def show_latest_reading(station=3):
    #breakpoint()
    return { 'current_weather' : Reading.objects.filter(station__exact=station).latest('reading_time') }