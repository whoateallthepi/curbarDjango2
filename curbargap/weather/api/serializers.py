from rest_framework import serializers
from ..models import Station, Reading

class ReadingSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Reading
#        fields = ['id', 'reading_time', 'station', 'wind_dir', 'wind_speed', 'wind_gust',
#            'wind_gust_dir', 'wind_speed_avg2m', 'wind_dir_avg2m', 'wind_gust_10m','wind_gust_dir_10m', 
#            'humidity','temperature', 'rain_1h', 'rain_today', 'rain_since_last', 'bar_uncorrected',
#             'bar_corrected', 'battery', 'light',]
    station_name = serializers.SerializerMethodField()
    class Meta:
        model = Reading
        fields = ['id', 'reading_time', 'station','station_name', 'wind_dir', 'wind_speed', 'wind_gust',
            'wind_gust_dir', 'wind_speed_avg2m', 'wind_dir_avg2m', 'wind_gust_10m','wind_gust_dir_10m', 
            'humidity','temperature', 'rain_1h', 'rain_today', 'rain_since_last', 'bar_uncorrected',
            'bar_corrected', 'battery', 'light',]
        
    def get_station_name(self, reading):
        return reading.station.name    

        
class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'name', 'latitude', 'longitude', 'altitude', 'type', ]