from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Product

class ProductTests(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=10.0,
            stock=100
        )

    def test_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_detail(self):
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Product")
