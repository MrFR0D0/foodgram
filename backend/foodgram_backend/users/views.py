from users.models import User
from rest_framework import viewsets
from api.serializers import UserSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    paginated_by = 2
    # permission_classes = (IsAdminOrStaff,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('=username',)
    # lookup_field = 'username'
    # http_method_names = ('get', 'post', 'patch', 'delete',)
