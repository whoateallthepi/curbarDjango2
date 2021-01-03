import django_filters
 
from .models import Reading

#class ReadingFilter(django_filters.FilterSet):
#    class Meta:
#        model = Reading
#        fields = ['station', 'reading_time', ]



class ReadingFilter(django_filters.FilterSet):
    reading_time = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Reading
        fields = ['station', 'reading_time', ]