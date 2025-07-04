from rest_framework.pagination import PageNumberPagination

from foodgram_backend import constants


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = constants.MAX_PAGE_SIZE
