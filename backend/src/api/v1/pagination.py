from rest_framework.pagination import PageNumberPagination

import constants


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация."""

    page_size_query_param = "limit"
    page_size = constants.MAX_PAGE_SIZE
