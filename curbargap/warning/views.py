from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, FormView, View
#from django.views.generic.edit import UpdateView
from django.contrib.gis.geos import Point
from .forms import MapForm
from .models import Warning
from django.conf import settings

from warning.models import Service, Warning

from django.utils import timezone

from warning.classes import Nswws

import json

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
    title = '' # used in template to display type of list 

    def get_queryset(self):
        status = self.request.GET.get('status', '1') # 0 = expired 1 = issued 3 = all
        in_force = self.request.GET.get('active', 'active') # test on date  all/current/historic
        area =  self.request.GET.get('area', 'all') # all / local
        order_by = self.request.GET.get('order', 'date') # date (start date) or 'closest'
        
        
        self.title = ''

        queryset = Warning.objects.all().order_by("validFromDate")
        #set up filters
        # status
        if status.isnumeric():
            st = int(status)
            if st < 2:
                queryset=queryset.filter(warningStatus=st)

            if st == 0:
                self.title = self.title + ' expired '
            elif st == 3:
                self.title = self.title + ' expired, current and cancelled'

        # no longer current
        if in_force == 'active':
            queryset = queryset.filter(validToDate__gte=timezone.now())
        else:
            self.title = self.title + ' includes historic '    
        
        if area == 'local':
            pnt = Point(settings.LONGITUDE,settings.LATITUDE)
            queryset = queryset.filter(geometry__contains=pnt)
            self.title = self.title + ' for ' + settings.LOCALITY
             
        #breakpoint()
        
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context['title'] = self.title
        return context    


class WarningDetailView(DetailView, FormView):
    context_object_name = 'warning' 
    form_class = MapForm
    queryset = Warning.objects.all()
    template_name = 'warning/warning/detail.html'
 
#def get_map(request):
    # we won't  get a post
#    if request.method == "POST":
#        print('post')
#    else:
#        form = MapForm(initial={"map": '{"type": "MultiPolygon", "coordinates": [[[[-2.6669, 54.0094], [-2.7219, 54.0175], [-2.9086, 54.0175], [-2.9883, 53.9997], [-3.0927, 53.8946], [-3.1174, 53.8444], [-3.1393, 53.799], [-3.1009, 53.7065], [-3.0075, 53.6577], [-2.8619, 53.5958], [-2.6587, 53.5583], [-2.5214, 53.5403], [-2.3566, 53.5175], [-2.2742, 53.4995], [-2.2028, 53.488], [-2.1423, 53.475], [-2.0792, 53.4603], [-2.016, 53.475], [-1.972, 53.5175], [-1.9254, 53.5517], [-1.8979, 53.5941], [-1.8979, 53.6739], [-1.9226, 53.7438], [-1.9501, 53.7763], [-2.0242, 53.8234], [-2.1725, 53.8833], [-2.2659, 53.9173], [-2.3126, 53.9383], [-2.4884, 53.9884], [-2.623, 54.0078], [-2.6669, 54.0094]]]]}'})    
#    
 #   return render(request, "detail.html", {"form": form})    


class FetchWarnings(View):
    template_name = 'warning/api/nswws_response.html'

    # this is an internal procedure to update the database from the 
    # data fetched from Nswws 
    def _store_updates(self, updates, service_id, feed_updated):
        def decodeWeatherType (weatherType):
            if weatherType == 'RAIN':
                return 0
            if weatherType == 'THUNDERSTORM':
                return 1
            if weatherType == 'WIND':
                return 2
            if weatherType == 'SNOW':
                return 3
            if weatherType == 'LIGHTNING':
                 return 4
            if weatherType == 'ICE':
                return 5
            if weatherType == 'EXTREME HEAT':
                return 6
            if weatherType == 'FOG':
                return 7
            return 8
        
        def decodeStatus(warningStatus):
            if warningStatus == 'EXPIRED':
                return 0
            if warningStatus == 'ISSUED':
                return 1
            if warningStatus == 'CANCELLED':
                return 2
            else:
                return 3
            
        def decodeLevel(warningLevel):
            if warningLevel == 'YELLOW':
                return 0
            if warningLevel == 'AMBER':
                return 1
            if warningLevel == 'RED':
                return 2
            
            return 3

        service = Service.objects.get(pk=service_id)
        for update in updates:
            
            # need to decode the weather types eg WIND >> 2
            wt = []
            for type in update['weatherType']:
                wt.append(decodeWeatherType(type))
            wte = ''
            
            # concatenate whatToExpect entries into one string
            for expect in update['whatToExpect']:
                wte = wte + expect + '. '

            warning = Warning(
                warningId = update['warningId'],
                service = service,
                issuedDate = update['issuedDate'],
                weatherType = wt,
                warningLikelihood = update['warningLikelihood'],
                warningLevel = decodeLevel(update['warningLevel']),
                warningStatus = decodeStatus(update['warningStatus']),
                warningHeadline = update['warningHeadline'],
                whatToExpect = wte,
                modifiedDate = update['modifiedDate'],
                validFromDate = update['validFromDate'],
                validToDate = update['validToDate'],
                affectedAreas = update['affectedAreas'],
                warningImpact = update['warningImpact'],
                geometry = json.dumps(update['geometry']),
                )
            #breakpoint()
            if warning.warningStatus == 3:
                print("**** unrecognised warningStatus")
                print(update['warningStatus'])

            warning.save()   
        
        service.lastUpdate = feed_updated
        service.save()
    
    def get(self, request, *args, **kwargs):
        force = self.request.GET.get('force', 'n')
        api_key = self.request.GET.get('api_key', '999')
        service_id =  self.request.GET.get('service_id', '1')

        f = force.startswith('y') or force.startswith('Y')

        if api_key != settings.WARNING_KEY:
            #message = 'API key error - no call made to Nswws'   
            return render (request, self.template_name, 
                           {'message': 'API key error - no call made to Nswws'}) 
        
        # create an instance of the Nswws connection
        n = Nswws(settings.NSWWS_API_KEY,settings.NSWWS_BASE_URL, settings.NSWWS_FEEDS_URL, service_id=1)
        
        # Get the service record for the last update
        service = Service.objects.get(pk=service_id)

        updates = n.check(service.lastUpdate) # check if there are any updates.
        f = (force.startswith('y') or force.startswith('Y'))
        
        if updates or f:
            uu = n.fetch_updates(force_all=f)
            # uu now contains a list of dicts of updates
            # store the updates
            self._store_updates(uu,service_id, n.feed_updated)
            
            message = 'API match - Nswws updates fetched'
            if f:
                message = message + ' force_all=y'
        else:
            message = 'API match - Nswws contacted - no updates'
        
        return render (request, self.template_name, {'message': message })        
        



