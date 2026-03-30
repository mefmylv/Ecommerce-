from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.products.models import Product

class CartViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CartSerializer

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.filter(id=cart.id)

    @extend_schema(responses={200: CartSerializer}, summary="Получить состав корзины")
    def list(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer'},
                'quantity': {'type': 'integer', 'default': 1}
            },
            'required': ['product_id']
        }},
        responses={201: CartSerializer},
        summary="Добавить товар в корзину"
    )
    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response(self.get_serializer(cart).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'quantity': {'type': 'integer'}
            },
            'required': ['quantity']
        }},
        responses={200: CartSerializer},
        summary="Изменить количество товара (по ID элемента)"
    )
    def update(self, request, *args, **kwargs):
        try:
            item_id = kwargs.get('pk')
            quantity = int(request.data.get('quantity'))
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.quantity = quantity
            item.save()
            return Response(self.get_serializer(item.cart).data)
        except (CartItem.DoesNotExist, KeyError, ValueError, TypeError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(summary="Удалить товар из корзины (по ID элемента)")
    def destroy(self, request, *args, **kwargs):
        try:
            item_id = kwargs.get('pk')
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
