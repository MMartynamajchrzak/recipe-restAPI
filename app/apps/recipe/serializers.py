from rest_framework import serializers
from apps.core.models import Tag, Ingredients


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
