# api/urls.py

from django.urls import path
from .views import EnergyDataList, EnergyDataUploadView

urlpatterns = [
    path('energy/', EnergyDataList.as_view(), name='energy-data-list'),
    path('energy/upload/', EnergyDataUploadView.as_view(), name='energy-data-upload'),
]