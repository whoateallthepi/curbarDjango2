from django.urls import path
from . import views

app_name = 'warning'

urlpatterns = [
    # service views
    path('service/',views.ServiceListView.as_view(), name='service_list'),
    path('service/<int:pk>/',views.ServiceDetailView.as_view(),name='service_detail'),
    path('warning/',views.WarningListView.as_view(),name='warning_list'),
    path('warning/<pk>/',views.WarningDetailView.as_view(),name='warning_detail'),
    path('api/fetch/',views.FetchWarnings.as_view(),name='fetch_warnings'),

    #path('forecast/<int:pk>', views.ForecastDetailView.as_view(), name='forecast_detail'),
    #path('forecast/api/fetchforecast/<api_key>', views.FetchForecasts.as_view(), name = 'fetch_forecast'),
    #path('forecast/summary', views.SummaryForecastView.as_view(), name='summary_forecast')
    #path('<int:year>/<int:month>/<int:day>/<slug:post>',
    #    views.post_detail,
    #    name='post_detail')
]