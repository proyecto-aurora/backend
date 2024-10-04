from django.contrib.auth.hashers import make_password, check_password
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .models import Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, Estados, Prioridad
from .serializers import (
    AreaSerializer, CargoSerializer, EmpleadosSerializer,
    ProyectoSerializer, TareasSerializer, SubtareaSerializer,
    EstadosSerializer, PrioridadSerializer, LoginSerializer, LogoutSerializer
)

# Vistas para los modelos
class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CargoViewSet(viewsets.ModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer

class EmpleadosViewSet(viewsets.ModelViewSet):
    queryset = Empleados.objects.all()
    serializer_class = EmpleadosSerializer

    def perform_create(self, serializer):
        """Sobrescribe el método perform_create para encriptar la contraseña antes de guardar"""
        contrasena = serializer.validated_data.get('contrasena')
        if contrasena:
            serializer.validated_data['contrasena'] = make_password(contrasena)
        serializer.save()

    def perform_update(self, serializer):
        """Sobrescribe el método perform_update para encriptar la contraseña al actualizar"""
        contrasena = serializer.validated_data.get('contrasena')
        if contrasena:
            serializer.validated_data['contrasena'] = make_password(contrasena)
        serializer.save()

# Vista para el Login
class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            return Response({
                'message': 'Login exitoso',
                'nombres': user.nombres,
                'apellidos': user.apellidos,
                'correo_electronico': user.correo_electronico,
                'celular': user.celular,
                'login': user.login,
                'cargo': user.cargo_id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

# Vista para el Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        # Aquí puedes añadir lógica adicional si es necesario, como invalidar tokens
        serializer = self.serializer_class()
        return Response(serializer.data, status=status.HTTP_200_OK)

# Vistas para el resto de los modelos
class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer

class TareasViewSet(viewsets.ModelViewSet):
    queryset = Tareas.objects.all()
    serializer_class = TareasSerializer

class SubtareaViewSet(viewsets.ModelViewSet):
    queryset = Subtarea.objects.all()
    serializer_class = SubtareaSerializer

class EstadosViewSet(viewsets.ModelViewSet):
    queryset = Estados.objects.all()
    serializer_class = EstadosSerializer

class PrioridadViewSet(viewsets.ModelViewSet):
    queryset = Prioridad.objects.all()
    serializer_class = PrioridadSerializer
