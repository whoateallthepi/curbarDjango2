from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Max, Min, Sum
from django.utils.timezone import datetime, timedelta
from django.utils import timezone

from .models import Reading, Forecast, Day, Timestep
from .forms import SearchReadingForm
from .classes import WeatherSummary
from .utils import rose, update_forecast 
from .tables import TimestepTable

from django.conf import settings

import datapoint

from collections import namedtuple

#from .filters import ReadingFilter

# Create your views here.
def reading_list (request):
    readings = Reading.objects.all().order_by('-reading_time')[0:20]
    return render(request,
                  'weather/reading/list.html',
                  {'readings' : readings })

def reading_detail (request, id):
    reading = get_object_or_404(Reading, id = id)
    return render (request,                
                   'weather/reading/detail.html',
                    {'reading' : reading})

def reading_search (request):
    form = SearchReadingForm()
    station = None
    date_from = None
    date_to = None
    result = []
    #breakpoint()
    if 'date_from' in request.GET:
        form = SearchReadingForm(request.GET)
        if form.is_valid():
            station = form.cleaned_data['station']
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            # create instance of WeatherSummary
            w = WeatherSummary(station, date_from, date_to)
            rain_1h = w.rain_1h()
            humidity = w.humidity()
            temperature = w.temperature()
            wind_speed = w.wind_speed()
            rain_total = w.rain_total()
            bar = w.bar()
            result = {**rain_1h, **humidity, **temperature, **wind_speed, **rain_total,
                      **bar }
            
    #breakpoint()                    
    return render(request,
                  'weather/reading/totals.html',
                  {'form': form,
                   'date_from': date_from,
                   'date_to': date_to,
                   'result' : result,
                   'station' : station,}) 

def forecast_view (request, station_id=351418):
    #
    # This is used for the summary forecast 
    #
    f = Forecast.objects.filter(location__exact=station_id).latest('forecast_time')
    station_name = f.name
    forecast_time = f.forecast_time
    d = Day.objects.filter(forecast__exact = f).order_by('date') 
    tables = [] # create a list of timestep objects
    dates = [] # create a list of dates - used in template
    past_3hrs = timezone.now() + timedelta(hours=-3)
    for delta in range(3):
         one_day = d.filter(date__date=(timezone.now() + timedelta(days=delta)))
         timesteps =  Timestep.objects.filter(day__in=one_day).filter(step_time__gt=past_3hrs).order_by('step_time') 
         #### create a list of 'table' objects ####
         tables.append(TimestepTable(timesteps, orderable=False))
         # the following rather depends on the forecasts
         # being updated today - could need a fix?
         dates.append(timezone.now() + timedelta(days=delta))

         # breakpoint()

    #django2_tables stuff
    #breakpoint()
    #table = tables[0]
    #breakpoint()
    return render (request,                
                   'weather/forecast/summary.html',
                    {'tables' : tables,
                    'dates' : dates,
                    'forecast_time' : forecast_time,
                    'station_name' : station_name,
                    }
                   )

def get_forecast (request, station_id):
    # To do - maybe some error checking!
    api_key = settings.DATAPOINT_API 
    station = station_id
    update_forecast(station, api_key)
    text = 'Updated forecast for station ' + str(station)
           
    return render (request,
                   'weather/api/forecast_response.html',
                   {'forecast_response' : text,
                   }
                   )


def regional_forecast_view(request, region_id):
    #
    # To do - add some error checking...
    #
    conn = datapoint.Manager(api_key=settings.DATAPOINT_API)    
    regions = conn.regions.get_all_regions()
    region_name = ''
    #maybe a better way of searching...
    for region in regions:
        if region.id == str(region_id):
            region_name = region.name
            break
    
    Forecast_section = namedtuple('Forecast_section', 'head text')
    forecast_sections = []

    forecast = conn.regions.get_raw_forecast(region_id) ['RegionalFcst']
    # Issued date is a string with 'T' delimiting time
    issued_str = forecast['issuedAt']
    fd,ft = issued_str.split('T')
    issued = datetime.strptime((fd + ' ' +ft), '%Y-%m-%d %H:%M:%S')
     
    sections = forecast['FcstPeriods']['Period']
    #breakpoint()
    for section in forecast ['FcstPeriods'] ['Period']:
        paragraph = []
        content = section['Paragraph']
        # deal with paragraphs containing multiple sections
        if isinstance(content, dict):
            paragraph.append(content)
        else:
            paragraph = content   
        
        #breakpoint()
        
        for line in paragraph: 
            #breakpoint()

            fs = Forecast_section (line['title'], line['$'])
            forecast_sections.append(fs) 

            #text = text + ('{}\n{}\n'.format(line['title'], line['$']))
             
    
    #breakpoint()
    
    return render (request,
                   'weather/forecast/full.html',
                   {'forecast' : forecast_sections,
                    'region'   : region_name,
                    'issued'   : issued,
                   }
                   )
def home_view(request):
   response = redirect('/forecast/forecast/summary') 
   return response 