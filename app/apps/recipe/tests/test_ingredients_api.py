from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Ingredients
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
