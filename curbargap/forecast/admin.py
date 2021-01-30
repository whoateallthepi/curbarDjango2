from django.contrib import admin

from .models import Forecast, TimeSeries, Symbol, Arrow

# Register your models here.

admin.site.register(Forecast)
admin.site.register(TimeSeries)
admin.site.register(Symbol)
admin.site.register(Arrow)