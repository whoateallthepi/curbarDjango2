from django.contrib import admin

from .models import Forecast, TimeSeries, Symbol

# Register your models here.

admin.site.register(Forecast)
admin.site.register(TimeSeries)
admin.site.register(Symbol)