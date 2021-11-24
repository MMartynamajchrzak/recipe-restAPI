from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.models import Tag, Recipe
from apps.recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    # Publicly available test API

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test login required for retrieving tags
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    # Tag tests for authorized users
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@email.com',
            password='test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        # test retrieving tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Gluten-free')

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        # test that tags returned are for authenticated user
        user2 = get_user_model().objects.create_user(
            'other@user.com',
            'otherpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Healthy')

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        # Test creating a new tag
        payload = {
            'name': 'Test tag'
        }
        self.client.post(TAGS_URL, payload)

        # returns bool
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        # Test creating a new tag with invalid payload
        payload = {
            'name': ''
        }
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        # test filtering tags by those assigned to recipes
        tag1 = Tag.objects.create(user=self.user, name='breakfast')
        tag2 = Tag.objects.create(user=self.user, name='supper')
        recipe = Recipe.objects.create(
            title='Sausages and eggs',
            time_minutes=10,
            price=7.00,
            user=self.user
        )
        recipe.tags.add(tag1)

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_tags_filtered_are_unique(self):
        # test that the filtered, listed tags are unique
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=15,
            price=5.00,
            user=self.user
        )
        recipe1.tags.add(tag)

        recipe2 = Recipe.objects.create(
            title='Spicy soup',
            time_minutes=40,
            price=4.00,
            user=self.user
        )
        recipe2.tags.add(tag)

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)
