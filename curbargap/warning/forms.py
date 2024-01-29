from django.contrib.gis.db import models
from django import forms
from django.contrib.gis.geos import GEOSGeometry
class MapForm(forms.Form):
    
    map = models.MultiPolygonField()