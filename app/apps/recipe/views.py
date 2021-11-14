from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.core.models import Tag
from .serializers import TagSerializer


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    # Manage tag in the db
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_queryset(self):
        # Returning objects for the authenticated user only
        return self.queryset.filter(user=self.request.user).order_by('-name')
