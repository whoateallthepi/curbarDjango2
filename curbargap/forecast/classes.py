from django.conf import settings
from forecast.models import Forecast, TimeSeries
import http.client
import json



class DataHub(object):
    
    def __init__(self, client_details=None, location = None, url = None):
        if client_details is None:
            self.headers = {
                'x-ibm-client-id': settings.DATAHUB_CLIENT_ID,
                'x-ibm-client-secret': settings.DATAHUB_CLIENT_SECRET,
                'accept': "application/json",
                 }
        else:
            self.headers = {
                'x-ibm-client-id': client_details[0],
                'x-ibm-client-secret': client_details[1],
                'accept': client_details[2],
             }
        if location is None:
            self.latitude = str(settings.LATITUDE)
            self.longitude = str(settings.LONGITUDE)
        else:
             self.latitude, self.longitude = location
        if url is None:
            self.datahub_url=settings.DATAHUB_URL
        else:
            self.datahub_url=url

        self._conn = http.client.HTTPSConnection(self.datahub_url)
        
    def close(self):
        self._conn.close()

    def fetch_spot_forecast(self, type=1):
        
        class ObjectView(object):
        # A utility to turn a dictionary into an object
            def __init__(self, d):
                self.__dict__ = d
        
        types = { 1 : 'hourly',
                  3 : 'three-hourly'}
        t = types[type]          

        
        self._conn.request("GET", 
                 "/metoffice/production/v0/forecasts/point/{type}"
                 "?excludeParameterMetadata=false&includeLocationName=true"
                 "&latitude={latitude}&longitude={longitude}"\
                     .format(type=t, latitude=self.latitude, longitude=self.longitude),
                     headers=self.headers)
    
        response = self._conn.getresponse()
        data = response.read()
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

