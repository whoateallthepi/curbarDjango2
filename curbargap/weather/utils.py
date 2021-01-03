from .models import Forecast, Day, Timestep
import datapoint
from django.db import connection

def rose(degrees):
      # Utility to convert degrees to a human direction 
    quadrants = ["N",
                 "NNE",
                 "NE",
                 "ENE",
                 "E",
                 "ESE",
                 "SE",
                 "SSE",
                 "S",
                 "SSW",
                 "SW",
                 "WSW",
                 "W",
                 "WNW",
                 "NW",
                 "NNW",
                 "N"
                   ]

    big_degrees = 371.25  + degrees
    quadrant = int(big_degrees/22.5)

    #force into range 0-15, with 0 = N 
    if quadrant >= 16:
       quadrant -= 16

    return quadrants[quadrant]

def update_forecast(station, api_key, type="3hourly"):

  conn = datapoint.connection(api_key=api_key)
  f = conn.get_forecast_for_site(station, type)

  forecast = Forecast(forecast_time=f.data_date,
                      location = f.id,
                      name = f.name)
  forecast.save()                    
  for dd in f.days:
    day = Day(forecast=forecast,
              date=dd.date)
    day.save()
    for ts in dd.timesteps:
      timestep = Timestep(day=day,
                          step_time = ts.date,
                          feels_like_temperature = ts.feels_like_temperature.value,
                          humidity = ts.humidity.value,
                          name = ts.name,
                          precipitation = ts.precipitation.value,
                          temperature = ts.temperature.value,
                          uv = ts.uv.value,
                          visibility = ts.visibility.value,
                          weather = ts.weather.value,
                          wind_direction = ts.wind_direction.value,
                          wind_gust = ts.wind_gust.value,
                          wind_speed = ts.wind_speed.value,)
      
      #breakpoint()
      timestep.save()

def get_symbol (self):
  # takes the met office 2 character and returns the url of
  # the matching symbol
  # WARNING - there is a better way of doing this - find it!

  with connection.cursor() as cursor:
    cursor.execute("SELECT symbol_image from weather_symbol where weather_symbol_key = '24';")
    row = cursor.fetchone()

  breakpoint()
  return row  

def get_weather(symbol):
      with connection.cursor() as cursor:
        cursor.execute("SELECT weather_type from weather_symbol where symbol_image = %s", [symbol])
        row = cursor.fetchone()
        #breakpoint()
      
      #breakpoint()
      return row [0]  