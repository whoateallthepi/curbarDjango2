from django import forms
from datetime import date


from chart.models import ChartRun, Chart, SatelliteImage

class ChartSearchForm(forms.Form):
        
        date = forms.DateField(initial=date.today)

class SatelliteSearchForm(forms.Form):
        
        date = forms.DateField(initial=date.today)
        type = forms.ChoiceField(choices = SatelliteImage.TYPES_OF_IMAGE, initial = SatelliteImage.SATELLITE_VISIBLE_N )
        

        

