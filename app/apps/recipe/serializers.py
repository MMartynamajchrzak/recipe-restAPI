from rest_framework import serializers
from apps.core.models import Tag, Ingredients, Recipe


class TagSerializer(serializers.ModelSerializer):
    # Serializer for tag objects
    class Meta:
        model = Tag
        fields = [
            'id',
            'name'
        ]
        read_only_fields = ['id', ]


class IngredientSerializer(serializers.ModelSerializer):
    # Serializer for ingredient object
    class Meta:
        model = Ingredients
        fields = [
            'id',
            'name'
        ]
        read_only_fields = ['id', ]


class RecipeSerializer(serializers.ModelSerializer):
    # Serializer for recipe object
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredients.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'ingredients',
            'tags',
            'time_minutes',
            'price',
            'link'
        ]
        read_only_fields = ['id', ]
