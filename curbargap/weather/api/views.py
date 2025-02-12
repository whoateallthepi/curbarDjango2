from rest_framework import generics
from ..models import Station, Reading
from .serializers import StationSerializer
from .serializers import ReadingSerializer

class StationListView(generics.ListAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

class StationDetailView(generics.RetrieveAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

class ReadingListView(generics.ListAPIView):
    queryset = Reading.objects.all()[:10]
    serializer_class = ReadingSerializer

class ReadingDetailView(generics.RetrieveAPIView):
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer

class ReadingLatestView(generics.RetrieveAPIView):
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer

    def get_object(self, *args, **kwargs):
        return self.queryset.filter(station=self.kwargs.get('station')).order_by('-reading_time')[0]

