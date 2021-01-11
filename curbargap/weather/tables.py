import django_tables2 as tables
from .models import Timestep, Symbol
from django.utils.html import format_html
from django.conf import settings
from .utils import get_weather

class ImageColumn(tables.Column):
        def render(self, value):
            wt = get_weather(value) # revisit this weird reverse lookup
            
            return format_html(
               '<img src="{url}" height="60px", width = "60px", class = "weather_symbol", alt = "{wt}", title = "{wt}" >',
                url=(settings.MEDIA_URL + value),
                wt=(wt)
                )
#'<img src="{url}" class="fav" height="20px", width="20px">',

class TimestepTable(tables.Table):
    #def __init__(self,*args,**kwargs):
    #    super().__init__(*args,**kwargs)
    #    self.base_columns['wind_direction'].verbose_name = 'Rose'
    
    date_header = 'date header'
    step_time = tables.DateTimeColumn(format ='gA')
    wind_direction = tables.Column(verbose_name = 'From')
    feels_like_temperature = tables.Column(verbose_name = 'Feel')
    #symbol = tables.Column(accessor='get_symbol',
    #                    verbose_name = 'Symbol')
    symbol = ImageColumn(accessor='get_symbol',
                           verbose_name = 'Weather')
                    
    class Meta:
        attrs = {"class": "table"}
        model = Timestep
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('step_time',
                  #'weather',
                  'symbol', 
                  'temperature', 
                  'feels_like_temperature',
                  'precipitation',
                  'wind_gust',
                  'wind_direction',
                  'uv',)
                  
        