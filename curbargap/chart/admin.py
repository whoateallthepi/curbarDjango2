from django.contrib import admin
from .models import Chart, ChartRun

# Register your models here.
admin.site.register(Chart)
admin.site.register(ChartRun)