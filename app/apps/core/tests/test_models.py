from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.core import models


def sample_user(email='test@email.com', password='test_pass'):
    # Create a sample user
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        # Test creating user with an email successful
        email = "test@email.com"
        password = "password123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test the email for a new user is normalized
        email = 'test@EMAIL.COM'
        user = get_user_model().objects.create_user(email, 'pass123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # Test creating user with no email raises error
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        # Test creating a new superuser
        user = get_user_model().objects.create_superuser(
            'test123@email.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        # Test the tag str representation
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        # Test the ingredient str representation
        ingredient = models.Ingredients.objects.create(
            user=sample_user(),
            name='Tomato'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        # Test the recipe str representation
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Cake with strawberries and vegan cream',
            time_minutes=60,
            price=30.00,
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        # test that image is saved in a correct location
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'

        self.assertEqual(file_path, expected_path)
