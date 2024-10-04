from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login as auth_login, logout
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from .models import Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, Estados, Prioridad
from .serializers import (
    AreaSerializer, CargoSerializer, EmpleadosSerializer,
    ProyectoSerializer, TareasSerializer, SubtareaSerializer,
    EstadosSerializer, PrioridadSerializer, LoginSerializer, LogoutSerializer
)

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Cambia a IsAuthenticated para requerir autenticación

class AreaViewSet(BaseViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class CargoViewSet(BaseViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer

class EmpleadosViewSet(BaseViewSet):
    queryset = Empleados.objects.all()
    serializer_class = EmpleadosSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        """Sobrescribe el método perform_update para encriptar la contraseña al actualizar"""
        contrasena = serializer.validated_data.get('contrasena')
        if contrasena:
            serializer.validated_data['contrasena'] = make_password(contrasena)
        serializer.save()

class ProyectoViewSet(BaseViewSet):
    queryset = Proyecto.objects.select_related('estados_id_estados', 'prioridad_id_prioridad').all()
    serializer_class = ProyectoSerializer

class TareasViewSet(BaseViewSet):
    queryset = Tareas.objects.all()
    serializer_class = TareasSerializer

class SubtareaViewSet(BaseViewSet):
    queryset = Subtarea.objects.all()
    serializer_class = SubtareaSerializer

class EstadosViewSet(BaseViewSet):
    queryset = Estados.objects.all()
    serializer_class = EstadosSerializer

class PrioridadViewSet(BaseViewSet):
    queryset = Prioridad.objects.all()
    serializer_class = PrioridadSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login = request.data.get('login')
        contrasena = request.data.get('contrasena')
        user = authenticate(request, username=login, password=contrasena)
        if user is not None:
            auth_login(request, user)
            return Response({'message': 'Login exitoso'}, status=status.HTTP_200_OK)
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
