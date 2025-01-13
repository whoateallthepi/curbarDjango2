from django.urls import path
from . import views

app_name = 'warning'
urlpatterns = [
    path('warnings/',
         views.WarningListView.as_view(),
         name = 'warning_list'),
    
    path('warnings/<pk>/',
         views.WarningListView.as_view(),
         name = 'warning_detail'),

    path('message/',
         views.IncomingMessageView.as_view(),
         name = 'incoming_message')
]