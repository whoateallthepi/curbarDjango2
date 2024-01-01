from django.contrib.gis import admin
from .models import Service, Warning

# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'lastUpdate')
    search_fields = ('name', 'lastUpdate')

@admin.register(Warning)
class WarningAdmin(admin.GISModelAdmin):
    list_display = ('warningId', 'warningStatus','issuedDate', 'weatherType','warningLevel','warningHeadline' )
    search_fields = ('warningId', 'warningLevel')    

