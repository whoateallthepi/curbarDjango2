from django.contrib.gis import admin
from .models import Service, Warning, Location, Device, Subscription

# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'lastUpdate')
    search_fields = ('name', 'lastUpdate')

@admin.register(Warning)
class WarningAdmin(admin.GISModelAdmin):
    list_display = ('warningId', 'warningStatus','issuedDate', 'notifiedDate','weatherType','warningLevel','warningHeadline' )
    search_fields = ('warningId', 'warningLevel')    

@admin.register(Location)
class LocationAdmin(admin.GISModelAdmin):
    list_display = ('id','name') 

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id','phoneNumber', 'type')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('type', 'device', 'location')