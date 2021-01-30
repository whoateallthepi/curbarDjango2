from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Station
from .models import Reading
from .models import Forecast
from .models import Day
from .models import Timestep
from .models import Symbol
from .models import Image

#admin.site.register(Station)
#admin.site.register(Reading)
@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
  list_display = ('name', 'altitude', 'type')


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
  list_display = ('station_id', 'reading_time' )
  list_filter = ('station_id', 'reading_time')

@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
  list_display = ('forecast_time', 'name')

@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
  list_display = ('forecast', 'date')

@admin.register(Timestep)
class TimestepAdmin(admin.ModelAdmin):
  list_display = ('step_time', 'temperature') 

@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
  list_display = [field.name for field in Symbol._meta.get_fields()]

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
  list_display = [field.name for field in Image._meta.get_fields()]  