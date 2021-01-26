from django.urls import path
from . import views

app_name = 'forecast'

urlpatterns = [
    # forecast views
    path('',views.ForecastListView.as_view(), name='forecast_list'),
    path('forecast/<int:pk>', views.ForecastDetailView.as_view(), name='forecast_detail'),
    path('forecast/api/fetchforecast/<api_key>', views.FetchHourlyForecast.as_view(), name = 'fetch_forecast'),
    path('forecast/summary', views.SummaryForecastView.as_view(), name='summary_forecast')
    #path('<int:year>/<int:month>/<int:day>/<slug:post>',
    #    views.post_detail,
    #    name='post_detail')
]