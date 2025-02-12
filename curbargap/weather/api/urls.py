from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('stations/',
         views.StationListView.as_view(),
         name = 'station_list',
         ),
    path('stations/<pk>/',
         views.StationDetailView.as_view(),
         name = 'station_detail',
         ),     
    path('readings/',
         views.ReadingListView.as_view(),
         name = 'reading_list',
         ), 

    path('readings/latest/<int:station>/', 
         views.ReadingLatestView.as_view(),
         name = 'reading_latest',
         ),  

    path('readings/<pk>/',
         views.ReadingDetailView.as_view(),
         name = 'reading_detail',
         ),           
]
