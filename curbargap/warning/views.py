from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, View

from warning.models import Service, Warning

# Create your views here.

class ServiceListView(ListView):
    model = Service
    context_object_name = 'services'
    paginate_by 10
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

class WarningDetailView(DetailView):
    context_object_name = 'warning' 
    queryset = Warning.objects.all()
    template_name = 'warning/warning/detail.html'      
