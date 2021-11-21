from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Recipe, Tag, Ingredients
from apps.recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    # Return recipe detail url
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Gluten-free'):
    # Create and return a sample tag
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Celery'):
    # Create and return a sample ingredient
    return Ingredients.objects.create(user=user, name=name)


def sample_recipe(user, **kwargs):
    # Create and return sample recipe
    defaults = {
        'title': 'Vanilla Cheesecake',
        'time_minutes': 90,
        'price': 30.00
    }

    defaults.update(**kwargs)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    # test unauthenticated user recipe access

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test that auth is required
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    # test authenticated recipe API access

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@email.com',
            'test_pass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        # test retrieving a list of recipes
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_auth_user(self):
        # test retrieving recipes for user
        user2 = get_user_model().objects.create_user(
            email='other@email.com',
            password='test12343'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user, title='Fish soup')

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)

    def test_view_recipe_detail(self):
        # test viewing a recipe detail
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)
