from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'weather'
urlpatterns = [
    
    path('bootstrap', TemplateView.as_view(template_name='weather/bootstrap/example.html')),
    path('about', TemplateView.as_view(template_name='weather/about.html')), 
    path('',views.reading_list, name = 'reading_list'),
    
    path('<int:id>/',
    views.reading_detail,
    name = 'reading_detail'),
    
    path('reading/totals',views.reading_search, name = 'reading_search'),

    path('forecast/summary/<int:station_id>',views.forecast_view, name = 'forecast_view'),
   
    path('forecast/full/<int:region_id>',views.regional_forecast_view, name = 'regional_forecast_view'),

    path('api/get_forecast/<int:station_id>', views.get_forecast, name = 'get_forecast'),

    path ('', views.home_view, name = 'home view')

]

