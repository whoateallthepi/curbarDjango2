from django import template
from django.utils.timezone import datetime, timedelta
from django.utils import timezone
from datetime import date

from ..models import Forecast, TimeSeries

from django.conf import settings
from ..utils import weather_codes

register = template.Library()

@register.inclusion_tag('forecast/forecast/latest.html')
def show_latest_forecast():
    past_hour = timezone.now() + timedelta(hours=-1)
    f = Forecast.objects.filter(type=1).latest('forecast_date')
    t =  f.timeseries_set.all().filter(series_time__gt=past_hour).earliest('series_time')
    
    return { 'current_symbol' : (settings.MEDIA_URL + t.get_symbol()),
             'weather_type' : weather_codes[t.significantWeatherCode], }