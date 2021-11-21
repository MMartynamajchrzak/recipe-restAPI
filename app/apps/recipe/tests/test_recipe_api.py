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

    def test_create_basic_recipe(self):
        # Test creating recipe
        payload = {
            'title': 'BBQ Steak',
            'time_minutes': 60,
            'price': 20.00
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags_assigned(self):
        # test creating a recipe with tags assigned
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Healthy')

        payload = {
            'title': 'Avocado toast',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 10,
            'price': 3.00
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        # test creating recipes with ingredients
        ingredient1 = sample_ingredient(user=self.user, name='Curry')
        ingredient2 = sample_ingredient(user=self.user, name='Lobster')
        payload = {
            'title': 'Lobster in curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 90,
            'price': 50.00
        }

        response = self.client.post(RECIPES_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        # test updating a recipe with patch
        # PATCH = update fields that are provided in a payload
        # not provided = not updated
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Spicy')

        payload = {
            'title': 'Chicken tikka',
            'tags': new_tag.id
        }

        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()

        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        # Test updating recipe with put
        # If we exclude a field from payload, this field will be emptied

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti',
            'time_minutes': 30,
            'price': 15.00
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
