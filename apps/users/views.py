from rest_framework import generics, permissions, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class RegisterView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    @extend_schema(responses={201: RegisterSerializer}, summary="Регистрация пользователя")
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ProfileView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    @extend_schema(responses={200: UserSerializer}, summary="Личный кабинет (Профиль)")
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}, summary="Выйти из аккаунта")
    def post(self, request):
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
