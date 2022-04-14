from django.urls import path
from . import views

app_name = 'chart'

urlpatterns = [
    # chart views
    path('',views.ChartListView.as_view(), name='chart_list'),
    path('chart/<int:pk>', views.ChartDetailView.as_view(), name='chart_detail'),
    path('chart/run/', views.ChartLatestSetView.as_view(), name='chart_run'),
    path('chart/search/', views.ChartSearchFormView.as_view(), name ='chart_search'),
    path('chart/api/fetch/<api_key>', views.FetchCharts.as_view(), name = 'fetch_charts'),
    path('satelliteimage/list',views.SatelliteImageListView.as_view(), name= 'satelliteimagelist'),
    path('satelliteimage/<int:pk>', views.SatelliteImageDetailView.as_view(),name='satelliteimage_detail'),
    path('satelliteimage/set/<type>/', views.SatelliteSetView.as_view(),name='satellite_set'),
    path('satelliteimage/search/',views.SatelliteSearchFormView.as_view(), name ='satellite_search'),
    path('satelliteimage/api/fetch/<api_key>/', views.FetchImages.as_view(), name = 'fetch_images'),
    
    
    #path('forecast/api/fetchforecast/<api_key>', views.FetchForecasts.as_view(), name = 'fetch_forecast'),
    #path('forecast/summary', views.SummaryForecastView.as_view(), name='summary_forecast')
    #path('<int:year>/<int:month>/<int:day>/<slug:post>',
    #    views.post_detail,
    #    name='post_detail')
]