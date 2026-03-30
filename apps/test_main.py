import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.cart.models import Cart, CartItem

User = get_user_model()

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user_data():
    return {"email": "test@example.com", "password": "password123"}

@pytest.fixture
def auth_client(api_client, user_data):
    User.objects.create_user(**user_data)
    response = api_client.post("/api/token/", user_data)
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

@pytest.mark.django_db
class TestAuthentication:
    def test_registration(self, api_client, user_data):
        response = api_client.post("/api/users/register/", user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=user_data['email']).exists()

    def test_login(self, api_client, user_data):
        User.objects.create_user(**user_data)
        response = api_client.post("/api/token/", user_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_profile_access(self, auth_client):
        response = auth_client.get("/api/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == "test@example.com"

@pytest.mark.django_db
class TestCart:
    @pytest.fixture
    def product(self):
        return Product.objects.create(name="Bread", price=50)

    def test_add_to_cart(self, auth_client, product):
        data = {"product_id": product.id, "quantity": 2}
        response = auth_client.post("/api/cart/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data['items']) == 1
        assert response.data['items'][0]['quantity'] == 2

    def test_update_quantity(self, auth_client, product):
        auth_client.post("/api/cart/", {"product_id": product.id, "quantity": 1})
        cart_item = CartItem.objects.first()
        
        response = auth_client.patch(f"/api/cart/{cart_item.id}/", {"quantity": 5})
        assert response.status_code == status.HTTP_200_OK
        # CartViewSet list logic is used in update/patch by default if not overridden, 
        # but here we check the DB directly for accuracy
        cart_item.refresh_from_db()
        assert cart_item.quantity == 5

    def test_total_price_calculation(self, auth_client):
        p1 = Product.objects.create(name="Milk", price=100)
        p2 = Product.objects.create(name="Egg", price=10)
        auth_client.post("/api/cart/", {"product_id": p1.id, "quantity": 2})
        auth_client.post("/api/cart/", {"product_id": p2.id, "quantity": 5})
        
        response = auth_client.get("/api/cart/")
        assert response.data['total_price'] == 250 # (100*2) + (10*5)

@pytest.mark.django_db
class TestSecurity:
    def test_unauthorized_access(self, api_client):
        endpoints = ["/api/users/me/", "/api/cart/"]
        for url in endpoints:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
