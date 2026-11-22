from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    """
    A custom pagination class that allows the user to specify
    the page size and returns a structured response.
    """
    page_size_query_param = 'page_size'  # e.g., /?page_size=5
    max_page_size = 1000 # A reasonable max limit for page size

    def get_paginated_response(self, data):
        """
        Overrides the default response format to provide more context.
        """
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total_results_in_query': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })