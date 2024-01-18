from django import template
from ..models import Warning, Service
from django.utils import timezone

from django.contrib.gis.geos import Point

from django.conf import settings

register = template.Library()
@register.inclusion_tag('warning/warning/current_warnings.html')
def show_current_warnings(service=settings.DEFAULT_WARNING_SERVICE):
    serv = Service.objects.get(pk=service)
    all_warnings = Warning.objects.filter(service=serv,warningStatus=1)
    all_non_expired = all_warnings.filter(warningStatus=1).filter(validToDate__gte=timezone.now()) # issued etc

    pnt = Point(settings.LONGITUDE,settings.LATITUDE)
           
    local_warnings = all_non_expired.filter(geometry__contains=pnt)

    other_warnings = all_non_expired.exclude(geometry__contains=pnt)

    return {'local_warnings': local_warnings,
            'other_warnings': other_warnings,
             'all_warnings' : all_non_expired,}

@register.inclusion_tag('warning/warning/alert.html')
def show_alert(service=settings.DEFAULT_WARNING_SERVICE):
    serv = Service.objects.get(pk=service)
    
    # get the highest, current, local warning 
    pnt = Point(settings.LONGITUDE,settings.LATITUDE)
    alert = Warning.objects.filter(service=serv,warningStatus=1).filter(validToDate__gte=timezone.now())
    alert = alert.filter(geometry__contains=pnt).order_by("-warningLevel")[:1]
    
    return {'alert': alert,}             
                        
