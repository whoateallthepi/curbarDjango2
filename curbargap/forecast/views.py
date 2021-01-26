from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, View
from django.utils.timezone import datetime, timedelta
from datetime import date

from forecast.models import Forecast, TimeSeries, Symbol
from django.conf import settings
from forecast.utils import fetch_hourly_forecast
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
 
class FetchHourlyForecast(View):

    template_name = 'forecast/forecast/fetch.html'

    def get(self, request, *args, **kwargs):
        api_key = kwargs['api_key']
        
        if api_key == settings.FORECAST_KEY:
            fetch_hourly_forecast()
            message = 'API matched - datahub contacted'
        else:
            message = 'API key failure'    
        
        return render (request, self.template_name, {'message': message })

class SummaryForecastView(View):
    template_name = 'forecast/forecast/summary.html'
    def get(self, request, *args, **kwargs):

        # first get latest forecast object
        f = Forecast.objects.latest('forecast_date')

        # then all the TimeSeries - earliest first is the default
        t =  f.timeseries_set.all()

        #Generate a list comp of 3 days from now ...  
        td = date.today()
    
        dates=[]
        # should be a listcomp
        for d in range (0,3):
            dates.append((td + timedelta(days=d)))
   
        # create a list to hold TimeSeries tables  
        tables = []
        for day in dates:
            timeseries = t.filter(series_time__date=day)
            tables.append(TimeSeriesTable(timeseries, orderable=False))

        return render (request, self.template_name, {'tables': tables })    
