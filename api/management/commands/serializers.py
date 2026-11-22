from rest_framework import serializers
from api.models import EnergyData

class EnergyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyData
        fields = '__all__' # This will include all fields from the model
