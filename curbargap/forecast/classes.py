from django.conf import settings
from forecast.models import Forecast, TimeSeries
import http.client
import json
import requests
import time



class DataHub(object):
    
    def __init__(self, api_key=None, location = None, url = None, retries=5):
        self.headers = {'accept':"application/json"}
        self.retries = retries
        if api_key == None:
            requestHeaders = {"apikey" : settings.DATAHUB_API_KEY}
        else: 
            requestHeaders = api_key 
        
        self.headers.update(requestHeaders)    
       
        if location is None:
            self.latitude = str(settings.LATITUDE)
            self.longitude = str(settings.LONGITUDE)
        else:
             self.latitude, self.longitude = location
        if url is None:
            self.datahub_url=settings.DATAHUB_URL
        else:
            self.datahub_url=url

        #self._conn = http.client.HTTPSConnection(self.datahub_url)
        
    def close(self):
        #self._conn.close()
        print("does nothing")

    def fetch_spot_forecast(self, type=1):
        class ObjectView(object):
        # A utility to turn a dictionary into an object
            def __init__(self, d):
                self.__dict__ = d
        
        types = { 1 : 'hourly',
                  3 : 'three-hourly'}
        t = types[type]

        parameters = { 
            'excludeParameterMetadata' : "FALSE",
            'includeLocationName' : "TRUE",
            'latitude' : str(self.latitude),
            'longitude' : str(self.longitude),
        } 
        
        success = False
        url = self.datahub_url + t

        for _ in range(self.retries):
            try:
                r = requests.get(url, headers=self.headers, params=parameters)
                success = True
            except Exception as e:
                print("** warning (retrying): %s",e)
                time.sleep(5)    
        if not success:
            # raise some error here - check Django docs
            print("retries exceeded contacting %s", url)
            return

        r.encoding = 'utf-8'

        data = r.text
        json_data = json.loads(data)
        #
        # convert the dictioanry to objects from here - avoids too many confusing indexes
        # 
        data_object = ObjectView(json_data)
    
        # Create objects with the details for the Forecast record in the model
        location_details = ObjectView(data_object.features[0]['geometry'])
    
        forecast_details = ObjectView(data_object.features[0]['properties'])
    
        forecast = Forecast( 
            type = type,
            latitude = location_details.coordinates[1],
            longitude = location_details.coordinates[0],
            name = forecast_details.location['name'],
            forecast_date = forecast_details.modelRunDate,
            distance = forecast_details.requestPointDistance,)
        #breakpoint()
        forecast.save() 
        #
        # For some reason, the three-hourly forecast uses feelsLikeTemp 
        # They also don't have a 'screenTemperature' so use 'maxScreenAirTemp'
        #
        if type == 3:
            flt_key = 'feelsLikeTemp'
            scrt_key='maxScreenAirTemp'
        else:
            flt_key = 'feelsLikeTemperature'
            scrt_key = 'screenTemperature'
        #     
        for ts in forecast_details.timeSeries:
            # use 'get' to access dictionary elements as not all values  
            # are in all forecasts
            #  
            # Some of these variables are dropped in the new API - post release
            # review the redundant ones.
            #
            timeseries = TimeSeries(
                forecast=forecast,
                feelsLikeTemperature=ts.get(flt_key),
                max10mWindGust=ts.get('max10mWindGust'),
                maxScreenAirTemp=ts.get('maxScreenAirTemp'),
                minScreenAirTemp=ts.get('minScreenAirTemp'),
                mslp=(int(ts['mslp'])/100),
                precipitationRate=ts.get('precipitationRate'),
                probOfPrecipitation=ts.get('probOfPrecipitation'),
                screenDewPointTemperature=ts.get('screenDewPointTemperature'),
                screenRelativeHumidity=ts.get('screenRelativeHumidity'),
                screenTemperature=ts.get(scrt_key),
                significantWeatherCode=ts.get('significantWeatherCode'),
                series_time=ts.get('time'),
                totalPrecipAmount=ts.get('totalPrecipAmount'),
                totalSnowAmount=ts.get('totalSnowAmount'),
                uvIndex=ts.get('uvIndex'),
                visibility=ts.get('visibility'),
                windDirectionFrom10m=ts.get('windDirectionFrom10m'),
                windGustSpeed10m=ts.get('windGustSpeed10m'),
                windSpeed10m=ts.get('windSpeed10m'),
                # following are unique to three-hourly forecasts
                probOfSnow=ts.get('probOfSnow'),
                probOfHeavySnow=ts.get('probOfHeavySnow'),
                probOfRain=ts.get('probOfRain'),
                probOfHeavyRain=ts.get('probOfHeavyRain'),
                probOfHail=ts.get('probOfHail'),
                probOfSferics=ts.get('probOfSferics')
                )
            timeseries.save()
    
        return None

