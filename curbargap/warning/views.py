from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, FormView, View
#from django.views.generic.edit import UpdateView
from django.contrib.gis.geos import Point
from .forms import MapForm
from .models import Warning
from django.conf import settings

from warning.models import Service, Warning

from django.utils import timezone

# Create your views here.

class ServiceListView(ListView):
    model = Service
    context_object_name = 'services'
    paginate_by = 10
    template_name = 'warning/service/list.html'

class ServiceDetailView(DetailView):
    context_object_name = 'service'  
    queryset = Service.objects.all()
    template_name = 'warning/service/detail.html' 

class WarningListView(ListView):
    model = Warning
    context_object_name = 'warnings'
    paginate_by = 20
    template_name = 'warning/warning/list.html' 

    def get_queryset(self):
        status = self.request.GET.get('status', '3') # 0 = expired 1 = issued 3 = all
        in_force = self.request.GET.get('active', 'all') # test on date  all/current/historic
        area =  self.request.GET.get('area', 'all') # all / local
        order_by = self.request.GET.get('order', 'date') # date (start date) or 'closest'
        
        queryset = Warning.objects.all()
        #set up filters
        # status
        if status.isnumeric():
            st = int(status)
            if st < 2:
                queryset=queryset.filter(warningStatus=st)
              
        # no longer current
        if in_force == 'active':
            queryset = queryset.filter(validToDate__gte=timezone.now())
        
        if area == 'local':
            pnt = Point(settings.LONGITUDE,settings.LATITUDE)
            queryset = queryset.filter(geometry__contains=pnt)
             
        #breakpoint()
        
        return queryset
        



class WarningDetailView(DetailView, FormView):
    context_object_name = 'warning' 
    form_class = MapForm
    queryset = Warning.objects.all()
    template_name = 'warning/warning/detail.html'
 
def get_map(request):
    # we won't  get a post
    if request.method == "POST":
        print('post')
    else:
        form = MapForm(initial={"map": '{"type": "MultiPolygon", "coordinates": [[[[-2.6669, 54.0094], [-2.7219, 54.0175], [-2.9086, 54.0175], [-2.9883, 53.9997], [-3.0927, 53.8946], [-3.1174, 53.8444], [-3.1393, 53.799], [-3.1009, 53.7065], [-3.0075, 53.6577], [-2.8619, 53.5958], [-2.6587, 53.5583], [-2.5214, 53.5403], [-2.3566, 53.5175], [-2.2742, 53.4995], [-2.2028, 53.488], [-2.1423, 53.475], [-2.0792, 53.4603], [-2.016, 53.475], [-1.972, 53.5175], [-1.9254, 53.5517], [-1.8979, 53.5941], [-1.8979, 53.6739], [-1.9226, 53.7438], [-1.9501, 53.7763], [-2.0242, 53.8234], [-2.1725, 53.8833], [-2.2659, 53.9173], [-2.3126, 53.9383], [-2.4884, 53.9884], [-2.623, 54.0078], [-2.6669, 54.0094]]]]}'})    
    
    return render(request, "detail.html", {"form": form})    
