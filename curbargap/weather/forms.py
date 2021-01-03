from django import forms
from .models import Reading, Station

class SearchReadingForm(forms.ModelForm):
    class Meta:
        model = Reading
        fields = ('station', 'date_from', 'date_to')
    
    station = forms.ModelChoiceField(queryset=Station.objects.all(), 
                                     empty_label=None, initial=3)    

    #station = forms.IntegerField()
    date_from = forms.DateField()
    date_to = forms.DateField()

#class SearchReadingForm(forms.Form):
#    station = forms.IntegerField()
#    date_from = forms.DateField()
#    date_to = forms.DateField()
