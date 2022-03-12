from django.conf import settings
from django.db import connection
from django.utils import dateparse
from .models import Chart, ChartRun, SatelliteImage

import http.client
import json

from datetime import timedelta

class DataPoint(object):
    
    def __init__(self, website = None, url = None, API_key = None):
        if website is None:
            website = settings.DATAPOINT_URL
        
        if API_key is None:
            API_key = settings.DATAPOINT_API

        self.conn = http.client.HTTPConnection(website)
        self.url = url
        self.API_key = API_key
     
    class _objectview(object):
        # A utility to turn a dictionary into an object
        def __init__(self, d):
            self.__dict__ = d

    def fetch_charts(self):
        
        if self.url is None:
           url = settings.CHARTS_URL
        else:
            url = self.url           
        
        self.conn.request("GET", url.format(datapoint_key=self.API_key))

        response = self.conn.getresponse()

        data = response.read()
    
        json_data = json.loads(data)
        #
        # convert the dictionary to objects from here - avoids too many confusing indexes
        # 
        data_object = self._objectview(json_data)
    
        pressure_charts = self._objectview(data_object.BWSurfacePressureChartList).BWSurfacePressureChart # full list  of charts

        chart_run_date = pressure_charts[0]['DataDate']  # all the charts have the same run date
        
        # breakpoint()
        # check if we have already processed this set 

        chart_run_check = ChartRun.objects.filter(date = chart_run_date)

        if chart_run_check:
            # have already processed this run - exit
            return
        
        chart_run = ChartRun(date=chart_run_date) 

        chart_run.save()
        
        for ch in pressure_charts:
            # is there a neater way of doing this??
            
            forecast_time = dateparse.parse_datetime (chart_run.date) + timedelta (hours=ch['ForecastPeriod']) # ForecastPeriod holds a delta from run date

            chart_uri =  ch['ProductURI'].format(key=settings.DATAPOINT_API)
            
        
            chart = Chart(run=chart_run,
                        type = 1,
                        valid_from = ch['ValidFrom'],
                        valid_to = ch['ValidTo'],
                        image_url = chart_uri,
                        forecast_time = forecast_time )
            chart.save()  
            
    def fetch_satellite(self):
        
        IMAGE_TYPES = SatelliteImage.TYPES_OF_IMAGE
        
        if self.url is None:
           url = settings.SATELLITES_URL
        else:
            url = self.url           
        
        self.conn.request("GET", url.format(datapoint_key=self.API_key))        
        
        response = self.conn.getresponse()

        data = response.read()

        json_data = json.loads(data)
        #
        # convert the dictioanry to objects from here - avoids too many confusing indexes
        # 
        data_object = self._objectview(json_data)

        ll = self._objectview(data_object.Layers)

        base_url = ll.BaseUrl['$']

        layers = ll.Layer # This produces a list of layers

        for layer in layers:
            displayName = layer['@displayName']
            service = layer['Service']
            layername = service ['LayerName'] # this is stored as 'type' in SatelliteImage 
            imageformat = service['ImageFormat']
            times = service['Times']['Time']  # now have a list of all times for chart
            type_code = 0
            # get the code for this layername

            for ii in IMAGE_TYPES:
                type_code_check, type_name = ii
                if type_name == layername:
                    type_code = type_code_check
                    break

            for image_time in times:
                
                # First check this is a new image 
                check_image = SatelliteImage.objects.filter(image_time=(image_time+'Z')).filter(type_code = type_code) # All times are GMT
                
                if not check_image:
                    # This is new - store it
                    si = SatelliteImage()
                    si.type_code = type_code
                    si.image_time =  dateparse.parse_datetime (image_time + 'Z')
                    si.image_url = base_url.format(key=settings.DATAPOINT_API, LayerName=layername, ImageFormat=imageformat, Time=(image_time))
                     
                    si.save()                



    def close(self):
            self.conn.close()

    