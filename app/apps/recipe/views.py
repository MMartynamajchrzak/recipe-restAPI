from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.core.models import Tag, Ingredients, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeDetailSerializer,\
    RecipeImageSerializer


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

    def _params_to_ints(self, _qs):
        # convert a list of string IDs to list of ints
        return [int(str_id) for str_id in _qs.split(',')]

    def get_queryset(self):
        # retrieve the queryset for the authenticated user
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        # gets serializer class for a different actions,requests
        # return appropriate serializer class
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        # create a new recipe
        serializer.save(user=self.request.user)

    @action(methods=['POST', ], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # upload an image to a recipe
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
