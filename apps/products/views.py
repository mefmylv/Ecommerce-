from rest_framework import generics, mixins, permissions
from drf_spectacular.utils import extend_schema
from .models import Product
from .serializers import ProductSerializer, ProductListSerializer

class ProductListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    permission_classes = (permissions.AllowAny,)

    @extend_schema(responses={200: ProductListSerializer(many=True)}, summary="Получить список всех товаров (карточки)")
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class ProductDetailView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.AllowAny,)

    @extend_schema(responses={200: ProductSerializer}, summary="Получить детальную информацию о товаре")
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
