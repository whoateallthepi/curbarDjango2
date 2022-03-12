from django.shortcuts import render
from django.utils import dateparse
from django.http import Http404

from django.shortcuts import get_object_or_404

from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

from django.views.generic import ListView, DetailView, TemplateView, View

from chart.models import Chart, ChartRun, SatelliteImage
from django.conf import settings
from chart.classes import DataPoint

from chart.forms import ChartSearchForm, SatelliteSearchForm
from django.views.generic.edit import FormView

from django.http import HttpResponseRedirect

class ChartListView(ListView):
    model = Chart
    context_object_name = 'charts'
    paginate_by = 8
    template_name = 'chart/chart/list.html'
    ordering = ['-forecast_time']

class ChartDetailView(DetailView):
    context_object_name = 'chart'
    queryset = Chart.objects.all()
    template_name = 'chart/chart/detail.html'


class ChartLatestSetView(View):
    template_name = 'chart/chart/run.html' 
    def get(self, request, *args, **kwargs):
        date = self.request.GET.get('date') or 'latest'
        
         # get latest ChartRun (or latest one for date)

        if date.lower() == 'latest':
            cr = ChartRun.objects.latest('date')
        else:
            date_p = dateparse.parse_date(date)
            if not date_p:
                raise Http404("Date parameter invalid and not 'latest'")
            else:
                
                try:
                    cr = ChartRun.objects.filter(date__date=date_p).latest('date')
                except ObjectDoesNotExist:
                    # create an empty queryset and return
                    charts = Chart.objects.none()
                    return render(request, self.template_name, {'charts': charts,} )
                         
        charts = cr.chart_set.all().order_by('forecast_time') #' no need to limit - usually only handful per day
        #breakpoint()
        return render(request, self.template_name, {'charts': charts,
                                                    'run_date': cr.date })

class SatelliteImageListView(ListView):
    model = SatelliteImage
    context_object_name = 'satelliteimages'
    paginate_by = 8
    template_name = 'chart/satellite/list.html'
    ordering = ['type_code','-image_time']

class SatelliteImageDetailView(DetailView):
    context_object_name = 'satelliteimage'
    queryset = SatelliteImage.objects.all()
    template_name = 'chart/satellite/detail.html'  

class SatelliteSetView(View):
    template_name = 'chart/satellite/set.html'
    def get(self, request, *args, **kwargs):
        type = kwargs['type']
        date = self.request.GET.get('date') or 'latest'
        
        if date.lower() == 'latest':
            satelliteimages = SatelliteImage.objects.all().filter(type_code=type)[:6]
        else:
            date_p = dateparse.parse_date(date)
            if not date_p:
                raise Http404("Date parameter invalid and not 'latest'")
            else:
                satelliteimages = SatelliteImage.objects.all().filter(image_time__date=date_p).filter(type_code=type)      
        
        return render(request, self.template_name,{ 'satelliteimages': satelliteimages })


class FetchCharts(View):

    template_name = 'chart/chart/fetch.html'

    def get(self, request, *args, **kwargs):
        api_key = kwargs['api_key']
        
        if api_key == settings.FORECAST_KEY:
            #create the Met Office DataHub connection 
            dp = DataPoint()
            dp.fetch_charts() 
            dp.close() 
            message = 'API matched - DataPoint contacted'
        else:
            message = 'API key failure'    
        
        return render (request, self.template_name, {'message': message })

class FetchImages(View):

    template_name = 'chart/satellite/fetch.html'

    def get(self, request, *args, **kwargs):
        api_key = kwargs['api_key']
        
        if api_key == settings.FORECAST_KEY:
            #create the Met Office DataHub connection 
            dp = DataPoint()
            dp.fetch_satellite() 
            dp.close() 
            message = 'API matched - DataPoint contacted'
        else:
            message = 'API key failure'    
        
        return render (request, self.template_name, {'message': message })        

class ChartSearchFormView(FormView):
   
    template_name = 'chart/chart/search.html'
    form_class = ChartSearchForm
    


    def form_valid(self,form):
        #breakpoint()
        redirect_url = "/chart/chart/run/?date=" + form.cleaned_data['date'].strftime('%Y-%m-%d')
        return  HttpResponseRedirect(redirect_url)
        #return super().form_valid(form)
        
class SatelliteSearchFormView(FormView):
   
    template_name = 'chart/satellite/search.html'
    form_class = SatelliteSearchForm
    


    def form_valid(self,form):
        
        redirect_url = "/chart/satelliteimage/set/" + form.cleaned_data['type'] + "/?date=" + form.cleaned_data['date'].strftime('%Y-%m-%d')
        return  HttpResponseRedirect(redirect_url)        
