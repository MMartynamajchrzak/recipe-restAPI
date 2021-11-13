from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**parameters):
    return get_user_model().objects.create_user(**parameters)


class PublicUserApiTests(TestCase):
    # Unauthenticated user from the internet gives the request
    # Test the user API Public

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        # Test creating user with valid payload is successful
        payload = {
            'email': 'test@email.com',
            'password': 'test123',
            'name': 'test_name'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        # Making sure password is encrypted
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        # Test creating a user that already exists fails
        payload = {
            'email': 'test@email.com',
            'password': 'test123',
            'name': 'test_name'
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        # Test password must be more than 5 characters
        payload = {
            'email': 'test@email.com',
            'password': 'test',
            'name': 'test_name'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the user wasn't created
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        # test that the token is created for the user
        payload = {
            'email': 'test@email.com',
            'password': 'test',
            'name': 'test_name'
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        # Test that token is not created if invalid credentials are given
        create_user(email='test@email.com', password='test_pass')
        payload = {
            'email': 'test@email.com',
            'password': 'wrong_password'
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        # Test that token is not created when user doesn't exist
        payload = {
            'email': 'test@email.com',
            'password': 'test',
            'name': 'test_name'
        }

        # not creating a user
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_missing_field(self):
        response = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
