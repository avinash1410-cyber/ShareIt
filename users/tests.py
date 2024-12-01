from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

# Dummy user creation or any necessary mocks could be added here.

class RegisterPageTestCase(APITestCase):
    def test_successful_registration(self):
        url = reverse('register')
        data = {
            'username': 'new_user',
            'password': 'validpassword',
            'email': 'test@example.com',
            'role': 'client'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Registration successful as a client user. Verification email sent to test@example.com.')

    def test_missing_username_or_password(self):
        url = reverse('register')  # Replace with the actual URL name of your register API
        data = {
            'password': 'validpassword',
            'role': 'client'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], 'Username, password, and email are required.')

    def test_invalid_role(self):
        url = reverse('register')  # Replace with the actual URL name of your register API
        data = {
            'username': 'new_user',
            'password': 'validpassword',
            'email': 'test@example.com',
            'role': 'invalid_role'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Invalid role. Role must be 'client' or 'operational'.")

