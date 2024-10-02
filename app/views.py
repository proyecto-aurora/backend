from django.contrib.auth.hashers import make_password, check_password
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, Estados, Prioridad
from .serializers import (
    AreaSerializer, CargoSerializer, EmpleadosSerializer,
    ProyectoSerializer, TareasSerializer, SubtareaSerializer,
    EstadosSerializer, PrioridadSerializer
)

# Vistas para los modelos
class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

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
    def post(self, request):
        # Obtener los datos de login y contraseña
        login = request.data.get('login')
        contrasena = request.data.get('contrasena')

        # Verificar si los campos login y contrasena están presentes
        if not login or not contrasena:
            return Response({'error': 'Por favor proporciona login y contraseña.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar el empleado por el campo de login
            empleado = Empleados.objects.get(login=login)
            
            # Validar la contraseña encriptada
            if check_password(contrasena, empleado.contrasena):
                # Retornar un mensaje de éxito y los datos del empleado
                return Response({
                    'message': 'Login exitoso',
                    'nombres': empleado.nombres,
                    'apellidos': empleado.apellidos,
                    'correo_electronico': empleado.correo_electronico,
                    'celular': empleado.celular,
                    'login': empleado.login,
                    'cargo': empleado.cargo_id
                    
                    
                }, status=status.HTTP_200_OK)
            else:
                # Retornar un error si la contraseña es incorrecta
                return Response({'mensaje': 'login o contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)
        except Empleados.DoesNotExist:
            # Retornar un error si el empleado no existe
            return Response({'mensaje': 'login o contraseña incorrecta'}, status=status.HTTP_404_NOT_FOUND)

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
