
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, View
from django.utils.timezone import datetime, timedelta
from django.utils import timezone
from datetime import date, time

from forecast.models import Forecast, TimeSeries, Symbol
from django.conf import settings
from forecast.classes import DataHub
from forecast.tables import TimeSeriesTable

# Create your views here.

class ForecastListView(ListView):
    model = Forecast
    context_object_name = 'forecasts'
    paginate_by = 5
    template_name = 'forecast/forecast/list.html'

class ForecastDetailView(DetailView):
    context_object_name = 'forecast'
    queryset = Forecast.objects.all() 
    template_name = 'forecast/forecast/detail.html'
 
class FetchForecasts(View):

    template_name = 'forecast/forecast/fetch.html'

    def get(self, request, *args, **kwargs):
        api_key = kwargs['api_key']
        
        if api_key == settings.FORECAST_KEY:
            #create the Met Office DataHub connection 
            dh = DataHub()
            dh.fetch_spot_forecast(type=3) # three-hourly forecast
            dh.fetch_spot_forecast(type=1)
            dh.close() 
            message = 'API matched - datahub contacted'
        else:
            message = 'API key failure'    
        
        return render (request, self.template_name, {'message': message })

class SummaryForecastView(View):
    template_name = 'forecast/forecast/summary.html'
    def get(self, request, *args, **kwargs):

        # first get latest  hourly forecast object
        f1 = Forecast.objects.filter(type=1).latest('forecast_date')

        # first get latest  3-hourly forecast object

        f3 = Forecast.objects.filter(type=3).latest('forecast_date')
  
        # then all the TimeSeries - earliest first is the default
        t1 = f1.timeseries_set.all()
        t3 = f3.timeseries_set.all()

        #Generate a list comp of 3 days from now ...  
        td = date.today()
    
        dates=[]
        # should be a listcomp
        for d in range (0,8):
            dates.append((td + timedelta(days=d)))
   
        past_hour = timezone.now() + timedelta(hours=-1)
        ninePM = time(21,00)

        
        tables = [] # create a list to hold TimeSeries tables  

        for day in dates[0:3]:
            timeseries = t1.filter(series_time__date=day).filter(series_time__gt=past_hour) # exclude expired forecasts
            # if the last of the timeseries is before 9pm - likely this is day 2 
            # (days go 0,1,2) and the houly forecsts are not a complete day. 
            # We need to fill in the rest of the day with data from the 3-hourly forecast
            #
            last_reading = timeseries[(len(timeseries)-1)].series_time
            if last_reading.time() < ninePM:
                timeseries_extra = t3.filter(series_time__date=day).filter(series_time__gt=last_reading)
                timeseries = timeseries|timeseries_extra

            tables.append(TimeSeriesTable(timeseries, orderable=False))                    

        # move on to process 3-day forecasts

        for day in dates [3:]:
            timeseries = t3.filter(series_time__date=day)
            tables.append(TimeSeriesTable(timeseries, orderable=False))
        #breakpoint()

        return render (request, self.template_name, {'tables': tables,
                                                     'dates': dates,
                                                     'issued' : f1.forecast_date,
                                                     'place' : f1.name })    
