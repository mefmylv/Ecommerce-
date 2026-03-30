from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.products.models import Product
from .models import Cart, CartItem

User = get_user_model()

class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword123')
        self.product = Product.objects.create(name='Test Product', price=10.0, stock=100)
        
        # Login
        response = self.client.post(reverse('token_obtain_pair'), {'email': 'test@example.com', 'password': 'testpassword123'})
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_add_to_cart(self):
        url = reverse('cart-list') # Using 'cart-list' for POST in ViewSet
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().quantity, 2)

    def test_list_cart(self):
        # First add something
        Cart.objects.get_or_create(user=self.user)
        cart = self.user.cart
        CartItem.objects.create(cart=cart, product=self.product, quantity=5)
        
        url = reverse('cart-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['quantity'], 5)

    def test_delete_from_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        
        url = reverse('cart-detail', args=[item.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)
