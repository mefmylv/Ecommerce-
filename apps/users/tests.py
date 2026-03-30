from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserTests(APITestCase):
    def test_registration(self):
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_login_and_profile(self):
        # Create user
        user = User.objects.create_user(email='test@example.com', password='testpassword123')
        
        # Login (Get Token)
        login_url = reverse('token_obtain_pair')
        login_data = {'email': 'test@example.com', 'password': 'testpassword123'}
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']

        # Get Profile
        profile_url = reverse('profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
