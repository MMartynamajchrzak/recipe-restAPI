from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.core.models import Tag, Ingredients, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer


class BaseRecipeViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):

    # Base ViewSet for user owned recipe attributes
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        # return objects for the authenticated user only
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        # Create a new object
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeViewSet):
    # Manage tag in the db

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeViewSet):
    # manage ingredients in the db

    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    # Manage recipes in the db
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        # retrieve the queryset for the authenticated user
        return self.queryset.filter(user=self.request.user)
