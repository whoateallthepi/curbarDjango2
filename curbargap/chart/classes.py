from django.conf import settings
from django.db import connection
from django.utils import dateparse
from dateparser import parse # more flexible parsing that django utils
from .models import Chart, ChartRun, SatelliteImage
from datetime import datetime, timedelta, timezone

from zoneinfo import ZoneInfo

import http.client
import json

import eumdac
import time
import fnmatch # all these for file download only
import io
import shutil
from tempfile import NamedTemporaryFile

import requests
from lxml.html import tostring, fromstring

class EUMetsat(object):
    
    def __init__(self, consumer_key = None, consumer_secret = None):
                
        if consumer_key is None:
            consumer_key = settings.EUMETSAT_CONSUMER_KEY
            consumer_secret = settings.EUMETSAT_CONSUMER_SECRET

        credentials = (consumer_key, consumer_secret)
        
        self.token = eumdac.AccessToken(credentials)
        self.datastore = None
        self.collection = None
        self.selected = None
        self.datatailor = None

        print(f"This token '{self.token}' expires {self.token.expiration}")

    def set_collection (self, product_name = 'EO:EUM:DAT:MSG:HRSEVIRI'):
        self.datastore = eumdac.DataStore(self.token)
        self.collection = self.datastore.get_collection(product_name)

    def get_first_in_collection (self):
        # don't pick anything up from past hour as we may not have the correct licence
        # and this will fail at the datatailor stage
        now = datetime.utcnow()
        latest_time = now - timedelta(hours=1)
        self.selected = self.collection.search(dtend=latest_time).first()

        #self.selected = self.collection.search().first()

    def list_chains (self, product='HRSEVIRI'):
        if self.datatailor is None:
            self.datatailor = eumdac.DataTailor(self.token) 

        for chain in self.datatailor.chains.search(product=product):
            print(chain)
            print('---')    

    def process_image (self, chain= 'nw_europe with quicklook', output_type = "*.png", write_to_DB = True):
        if self.datatailor is None:
            self.datatailor = eumdac.DataTailor(self.token) 
        #breakpoint()
        ch =  self.datatailor.chains.read(chain)
        # Run the customnisation
        #breakpoint()
        customisation = self.datatailor.new_customisation(self.selected, chain=ch)

        print(f'The status of the customisation is {customisation.status}.')
        while int(customisation.progress) < 100:
            print(f'The progress of the customisation is: {customisation.progress}%')
            time.sleep(2)

        file_name, =  fnmatch.filter(customisation.outputs, output_type)  

        with customisation.stream_output(file_name,) as stream,  NamedTemporaryFile(delete=True) as tempfile: #,  open(stream.name, mode='wb') as fdst:
            #file = tempfile.SpooledTemporaryFile()
            #file = io.BytesIO()
            shutil.copyfileobj(stream, tempfile)
            
            if write_to_DB:
                # Create a Django object
                s_image = SatelliteImage(type_code = SatelliteImage.EUMETSAT,
                                        image_time = self.selected.sensing_end.replace(tzinfo=ZoneInfo('UTC')),
                                        image_url = tempfile.name, # this will be a /tmp/...etc
                                        #image_file = tempfile,
                                        processing_details = ch.filter)
                s_image.save()
            
            customisation.delete()    

    def clear_datatailor(self):   
        if self.datatailor is None:
            self.datatailor = eumdac.DataTailor(self.token)

        for customisation in self.datatailor.customisations:
           try: 
               customisation.delete()
           except eumdac.customisation.CustomisationError as error:
               print("Customisation Error:", error)
           except Exception as error:
               print("Unexpected error:", error)

class MetOfficeWeb(object):
# DataPoint is being withdrawn so adding in a new class to 
# screen scrape from Met Office website where equivalen info is unavailable from 
# from the replacement DataHub.
# Initially we are getting synoptic charts and text forecasts.
#
    def __init__(self, charts_URL = None):
        if charts_URL is None:
            self.charts_URL = settings.CHARTS_URL
        else:
            self.charts_URL = charts_URL    

    def fetch_charts(self):

        def scrape_charts (type=Chart.COLOUR_SURFACE, create_Chart_Run=True):
            #
            # B&W and colour charts basically use the same code. However the Chart_Run record only 
            # needs creating once. So call for colour with create_Chart_Run = True
            # then call for B&W with create_Chart_Run = False
            # If called with create_Chart_Run = True and the chart run already exists - return False
            # - indicates Chart_Run already exists and there is no need to get the charts. 
            # Otherwise return True.
            #
            # Possible future fix - maybe make ChartRun unique in model as this is done in code, currently
            #
            response = requests.get(self.charts_URL)

            if response.status_code != 200:
                return ConnectionError ("Failed to connect to URL %s", self.charts_URL)
            
            page = fromstring(response.text)

            match type:
                case Chart.COLOUR_SURFACE:
                    element_id = 'colourCharts'
                case Chart.BW_SURFACE:
                    element_id = 'bwCharts'    
                case _:
                    element_id = 'colourCharts'    

            ulist =  page.get_element_by_id(element_id)

            charts = [] # will be a list of tuples (date,url)

            for uu in ulist:
                link = tostring(uu).decode('utf-8')
                dd = (link[(link.find('data-value=') + 12)::])
                ds = dd.split('"') # creates a list - zero element  is date, index 2 element is url

                # following line is a British Summer Time fudge as dateparser baulks at UTC+ timezones
                this_date = ds[0] 
                subtract_BST = 'UTC+1' in this_date
                if subtract_BST:
                    this_date = this_date.replace('(UTC+1)','UTC') # otherwise this messes up parse

                td = parse(this_date) # .astimezone(timezone.utc) # now a datetime object

                if subtract_BST:
                    td -= timedelta(hours=1)
                # now have a timezone date corrected for BST if required 
                
                charts.append((td, ds[2]))

            chart_run_date, _ = charts[0] # the datetime of the first chart is always the origin time of the
                                        # set of charts

            if create_Chart_Run:
                if ChartRun.objects.filter(date = chart_run_date):
                    print(f'Chart run already exists {chart_run_date} - exiting')
                    return False

                chart_run = ChartRun(date=chart_run_date) 
                chart_run.save()

            # re - obtain the ChartRun we need to hang the charts off
            #     
            chart_run = ChartRun.objects.get(date=chart_run_date) # should only be one but perhaps
                                                                  # enforce in model?
            for ch in charts:
                chart_time, chart_uri = ch
                chart = Chart(run=chart_run,
                            type = type,
                            #valid_from = chart_run_date,
                            #valid_to = chart_time,
                            image_url = chart_uri,
                            forecast_time = chart_time )
                #breakpoint()
                chart.save() 

            return True  # indicates a Chart_Run has been either created or was expected    
        #
        # here is the actual processing
        #
        if  scrape_charts( type = Chart.COLOUR_SURFACE, create_Chart_Run=True):
            # We successfully scraped the colour charts now try the B&Ws
            scrape_charts( type = Chart.BW_SURFACE, create_Chart_Run=False)
            
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

    
