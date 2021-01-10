from django import template
from ..models import Status

register = template.Library()

@register.inclusion_tag('weather/station/current_status.html')
def show_latest_status(station=3):
    s = Status.objects.filter(station__exact=station).latest('created')
    status_full = s.STATUS[(s.status -1 )] [1] # this is hideous - find a better way
    #breakpoint()
    return { 'current_status' : Status.objects.filter(station__exact=station).latest('created'),
            'status_full'   :  status_full
     }