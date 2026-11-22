from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from api.models import EnergyData
from api.management.commands.serializers import EnergyDataSerializer
from api.pageination import CustomPagination
from api.etl import process_energy_csv
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class EnergyDataList(generics.ListAPIView):
    queryset = EnergyData.objects.all()
    serializer_class = EnergyDataSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'date_time': ['exact', 'year', 'month', 'day'],
        'gas': ['exact', 'gt', 'lt'],
        'nuclear': ['exact', 'gt', 'lt'],
        'solar': ['exact', 'gt', 'lt'],
        'wind_perc': ['exact', 'gt', 'lt'],
        'carbon_intensity': ['exact', 'gt', 'lt'],
    }
    ordering_fields = ['date_time', 'carbon_intensity', 'gas', 'solar', 'wind_perc']

    def list(self, request, *args, **kwargs):
        filtered_queryset = self.filter_queryset(self.get_queryset())
        total_limit_str = request.query_params.get('total_limit')
        if total_limit_str is not None:
            try:
                limit = int(total_limit_str)
                if limit == 0:
                    serializer = self.get_serializer(filtered_queryset, many=True)
                    return Response(serializer.data)
                elif limit > 0:
                    sliced_queryset = filtered_queryset[:limit]
                    serializer = self.get_serializer(sliced_queryset, many=True)
                    return Response(serializer.data)
            except (ValueError, TypeError):
                pass
        
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)

class EnergyDataUploadView(APIView):
    """
    An endpoint for uploading a CSV file to refresh the energy dataset.
    """
    # Use MultiPartParser for standard file uploads
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.data['file']
        
        # Call the ETL function
        result = process_energy_csv(file_obj)

        if result['status'] == 'success':
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)