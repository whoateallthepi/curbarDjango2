from django import template
from ..models import Warning, Service
from django.utils import timezone

from django.contrib.gis.geos import Point

from django.conf import settings

register = template.Library()

@register.inclusion_tag('warning/warning/current_warnings.html')
def show_current_warnings(service=settings.DEFAULT_WARNING_SERVICE):
    serv = Service.objects.get(pk=service)
    all_warnings = Warning.objects.filter(service=serv,warningStatus=1).order_by("validFromDate")
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
                        
@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    It also removes any empty parameters to keep things neat,
    so you can remove a parm by setting it to ``""``.

    For example, if you're on the page ``/things/?with_frosting=true&page=5``,
    then

    <a href="/things/?{% param_replace page=3 %}">Page 3</a>

    would expand to

    <a href="/things/?with_frosting=true&page=3">Page 3</a>

    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()                        
