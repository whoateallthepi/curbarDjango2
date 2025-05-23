from rest_framework import serializers
from ..models import Warning
class WarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warning
        fields = ['warningId', 'weatherType', 'issuedDate']