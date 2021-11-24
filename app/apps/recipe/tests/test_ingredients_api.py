from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Ingredients, Recipe
from apps.recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredients-list')


class PublicIngredientsAPITests(TestCase):
    # Test publicly available ingredients API

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that login is required to access the ingredients
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    # test the private ingredients API
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@email.com',
            password='test_pass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        # test retrieving a list of ingredients
        Ingredients.objects.create(user=self.user, name='Kale')
        Ingredients.objects.create(user=self.user, name='Pineapple')

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        # test that only ingredients for the authenticated user are returned
        user2 = get_user_model().objects.create_user('seconduser@emai.com', 'second_pass')
        Ingredients.objects.create(user=user2, name='Milk')

        ingredient = Ingredients.objects.create(user=self.user, name='Spinach')

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], ingredient.name)

    def test_create_ingredients_successful(self):
        # Test create a new ingredient
        payload = {
            'name': 'pumpkin'
        }
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredients.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        # test creating invalid ingredients fails
        payload = {
            'name': ''
        }
        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        # test filtering ingredients by those assigned to recipes
        ingredient1 = Ingredients.objects.create(
            user=self.user, name='apples'
        )
        ingredient2 = Ingredients.objects.create(
            user=self.user, name='Turkey'
        )
        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=60,
            price=10.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_ingredient_assigned_unique(self):
        # test filtering ingredients by assigned returns unique items
        ingredient = Ingredients.objects.create(
            user=self.user,
            name='eggs'
        )
        Ingredients.objects.create(user=self.user, name='milk')
        recipe1 = Recipe.objects.create(
            title='Hard eggs',
            time_minutes=10,
            price=3.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Eggs on toast',
            time_minutes=10,
            price=3.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)

