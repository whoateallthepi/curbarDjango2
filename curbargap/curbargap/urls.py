"""curbargap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from weather import views
from warning import views as warning_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('weather/', include('weather.urls', namespace='weather')),
    path ('', views.home_view, name = 'home view'),
    path('blog/', include('blog.urls', namespace='blog')),
    path('forecast/', include ('forecast.urls', namespace='forecast')),
    path('chart/', include ('chart.urls', namespace='chart')),
    path('warning/', include('warning.urls',namespace='warning')),
    path('api/', include('warning.api.urls', namespace='api')),
    path('w/<str:url_hash>', warning_views.redirect_view, name='redirect'), 



]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL,
                        document_root=settings.MEDIA_ROOT)
