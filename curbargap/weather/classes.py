from django.db.models import Avg, Max, Min, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Reading, Forecast, Timestep, Day, Symbol
from .utils import rose, get_symbol
from datetime import timedelta

class LatestForecast (object):
    # Would be sensible to rewrite with forecast_view 
    def __init__(self, station=351418): 
        f = Forecast.objects.filter(location__exact=station).latest('forecast_time')
        station_name = f.name
        forecast_time = f.forecast_time
        d = Day.objects.filter(forecast__exact = f).filter(date__date=(timezone.now())) 
        past_3hrs = timezone.now() + timedelta(hours=-3)
        timestep =  Timestep.objects.filter(day__in=d).filter(step_time__gt=past_3hrs).earliest('step_time')
        #breakpoint()
        symbol = get_object_or_404(Symbol, symbol_key=timestep.weather) 
        self.symbol=symbol.symbol_image.url
        self.symbol_key = symbol.symbol_key
        self.weather_type = symbol.weather_type

class LatestReading(object):
    def __init__(self, station=3):
        self.reading = (Reading.objects.filter(station__exact=station).latest('reading_time'))         
        
class WeatherSummary(object):
    'Class to produce summary reports for a time period'
    def __init__(self, station, date_from, date_to):
        self.station = station
        self.date_from = date_from
        # at the moment we are only processing dates - not times
        # when the queryset is generated it implicity adds 00:00:00 to make it a 
        # datetime as per the model. This omits the current day. As a fix
        # add a day to the date_to - this will need revisiting if we redevelop to 
        # include times 
        self.date_to = (date_to + timedelta(days=1))

        # build date range and station filter
        self.date_station_query = (Reading.objects.filter(station__exact=self.station)
                                  .exclude(reading_time__lt=self.date_from)
                                  .exclude(reading_time__gt=self.date_to))

    def get_max (self, field):
        # takes a field name and returns the Reading with the max value 
        # to do - add some validation!
        reading = self.date_station_query.latest(field)
        return reading
         
    def rain_1h (self):
        query = rain_1h_max = self.date_station_query.exclude(rain_1h__isnull=True).latest('rain_1h')
        rain_1h_max = query.rain_1h
        rain_1h_time = query.reading_time   
        return { 'rain_1h_max' : rain_1h_max, 
                  'rain_1h_max_time' : rain_1h_time, } 
    def humidity (self):
        query_base = self.date_station_query.exclude(humidity__isnull=True)
        query = query_base.latest('humidity')
        humidity_max = query.humidity
        humidity_max_time = query.reading_time  
        query2 = query_base.earliest('humidity')
        humidity_min = query2.humidity
        humidity_min_time = query2.reading_time 
        return { 'humidity_max' : humidity_max, 
                 'humidity_max_time' : humidity_max_time,
                 'humidity_min' : humidity_min,
                 'humidity_min_time' : humidity_min_time }

    def temperature (self):
        query = self.date_station_query.latest('temperature')
        temperature_max = query.temperature
        temperature_max_time = query.reading_time  
        query2 = self.date_station_query.earliest('temperature')
        temperature_min = query2.temperature
        temperature_min_time = query2.reading_time 
        return { 'temperature_max' : temperature_max, 
                 'temperature_max_time' : temperature_max_time,
                 'temperature_min' : temperature_min,
                 'temperature_min_time' : temperature_min_time }    

    def bar (self):
        query = self.date_station_query.latest('bar_corrected')
        bar_max = query.bar_corrected
        bar_max_time = query.reading_time  
        query2 = self.date_station_query.earliest('bar_corrected')
        bar_min = query2.bar_corrected
        bar_min_time = query2.reading_time 
        return { 'bar_max' : bar_max, 
                 'bar_max_time' : bar_max_time,
                 'bar_min' : bar_min,
                 'bar_min_time' : bar_min_time }      

    def wind_speed(self):
        query = self.date_station_query.latest('wind_speed')
        wind_max = query.wind_speed
        wind_max_time = query.reading_time  
        wind_max_dir = query.wind_dir 
        wind_max_rose = rose(wind_max_dir)
        query2 = self.date_station_query.latest('wind_speed_avg2m') 
        wind_avg2m_max = query2.wind_speed_avg2m
        wind_avg2m_max_time = query2.reading_time
        wind_avg2m_dir = query2.wind_dir_avg2m
        wind_avg2m_rose = rose(wind_avg2m_dir)
        return { 'wind_max' : wind_max, 
                 'wind_max_time' : wind_max_time,
                 'wind_max_dir'  : wind_max_dir,
                 'wind_max_rose' : wind_max_rose,
                 'wind_avg2m_max': wind_avg2m_max,
                 'wind_avg2m_max_time' : wind_avg2m_max_time,
                 'wind_avg2m_dir' : wind_avg2m_dir,
                'wind_avg2m_rose' : wind_avg2m_rose }    

    def rain_total (self):
        total = self.date_station_query.aggregate(Sum('rain_since_last'))
        rain_total = total['rain_since_last__sum']
        return { 'rain_total' : rain_total, }

class AstroData(object):
    def __init__(self, latitude, longitude, date):
        pass