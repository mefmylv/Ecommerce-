from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductSerializer, ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price', 'updated_at')

    def get_total_price(self, obj) -> float:
        return sum(item.product.price * item.quantity for item in obj.items.all())
