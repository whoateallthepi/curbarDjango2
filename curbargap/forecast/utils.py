from django.conf import settings
from forecast.models import Forecast, TimeSeries
import http.client
import json

weather_codes = {
    0: "Clear night",
    1: "Sunny day",
    2: "Partly cloudy (night)",
    3: "Partly cloudy (day)",
    4: "Not used",
    5: "Mist",
    6: "Fog",
    7: "Cloudy",
    8: "Overcast",
    9: "Light rain shower (night)",
    10: "Light rain shower (day)",
    11: "Drizzle",
    12: "Light rain",
    13: "Heavy rain shower (night)",
    14: "Heavy rain shower (day)",
    15: "Heavy rain",
    16: "Sleet shower (night)",
    17: "Sleet shower (day)",
    18: "Sleet",
    19: "Hail shower (night)",
    20: "Hail shower (day)",
    21: "Hail",
    22: "Light snow shower (night)",
    23: "Light snow shower (day)",
    24: "Light snow",
    25: "Heavy snow shower (night)",
    26: "Heavy snow shower (day)",
    27: "Heavy snow",
    28: "Thunder shower (night)",
    29: "Thunder shower (day)",
    30: "Thunder",
}


class ObjectView(object):
    # A utility to turn a dictionary into an object
    def __init__(self, d):
        self.__dict__ = d

def fetch_hourly_forecast():
    # Fetches an hourly forecast from the met office DataHub 
    conn = http.client.HTTPSConnection(settings.DATAHUB_URL)

    headers = {
    'x-ibm-client-id': settings.DATAHUB_CLIENT_ID,
    'x-ibm-client-secret': settings.DATAHUB_CLIENT_SECRET,
    'accept': "application/json",
        }

    latitude = str(settings.LATITUDE)
    longitude = str(settings.LONGITUDE)

    conn.request("GET", 
                 "/metoffice/production/v0/forecasts/point/hourly"
                 "?excludeParameterMetadata=false&includeLocationName=true"
                 "&latitude={latitude}&longitude={longitude}".format(latitude=latitude, longitude=longitude),
                headers=headers)
    
    response = conn.getresponse()
    data = response.read()
    json_data = json.loads(data)
    #
    # convert the dictioanry to objects from here - avoids too many confusing indexes
    # 
    data_object = ObjectView(json_data)
    
    # Create objects with the details for the Forecast record in the model
    location_details = ObjectView(data_object.features[0]['geometry'])
    
    forecast_details = ObjectView(data_object.features[0]['properties'])
    
    forecast = Forecast( latitude = location_details.coordinates[1],
                         longitude = location_details.coordinates[0],
                         name = forecast_details.location['name'],
                         forecast_date = forecast_details.modelRunDate,
                         distance = forecast_details.requestPointDistance,)
    forecast.save() 
    
    for ts in forecast_details.timeSeries:
        # deal with the variables not in all forecasts (better way?)
        
        if 'max10mWindGust' in ts:
            max10mWindGust = ts['max10mWindGust'] 
        else:
            max10mWindGust = None
        
        if 'maxScreenAirTemp' in ts:
            maxScreenAirTemp = ts['maxScreenAirTemp'] 
        else:
            maxScreenAirTemp = None
        
        if 'minScreenAirTemp' in ts:
            minScreenAirTemp = ts['minScreenAirTemp'] 
        else:
            minScreenAirTemp = None        

        timeseries = TimeSeries(forecast=forecast,
                                feelsLikeTemperature=ts['feelsLikeTemperature'],
                                max10mWindGust=max10mWindGust,
                                maxScreenAirTemp=maxScreenAirTemp,
                                minScreenAirTemp=minScreenAirTemp,
                                mslp=(int(ts['mslp'])/100),
                                precipitationRate=ts['precipitationRate'],
                                probOfPrecipitation=ts['probOfPrecipitation'],
                                screenDewPointTemperature=ts['screenDewPointTemperature'],
                                screenRelativeHumidity=ts['screenRelativeHumidity'],
                                screenTemperature=ts['screenTemperature'],
                                significantWeatherCode=ts['significantWeatherCode'],
                                series_time=ts['time'],
                                totalPrecipAmount=ts['totalPrecipAmount'],
                                totalSnowAmount=ts['totalSnowAmount'],
                                uvIndex=ts['uvIndex'],
                                visibility=ts['visibility'],
                                windDirectionFrom10m=ts['windDirectionFrom10m'],
                                windGustSpeed10m=ts['windGustSpeed10m'],
                                windSpeed10m=ts['windSpeed10m'],
        )
        timeseries.save()
    
    return None

