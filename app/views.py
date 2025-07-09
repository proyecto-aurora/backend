"""
Vistas de la API REST para el sistema Aurora.

Este módulo contiene todas las vistas para gestionar:
- Autenticación de empleados
- CRUD de empleados, áreas, cargos
- Gestión de proyectos, tareas y subtareas
- Estados y prioridades

Utiliza Django REST Framework para proporcionar una API RESTful completa.

Autor: Equipo de Desarrollo Aurora
Fecha: 2024
"""

import logging
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils import timezone
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, 
    Estados, Prioridad, EmpleadosProyecto
)
from .serializers import (
    AreaSerializer, CargoSerializer, EmpleadosSerializer,
    ProyectoSerializer, TareasSerializer, SubtareaSerializer,
    EstadosSerializer, PrioridadSerializer, LoginSerializer, 
    LogoutSerializer, EmpleadosProyectoSerializer
)

# Configurar logging
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginación estándar para todas las vistas.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base con configuraciones comunes para todos los endpoints.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_serializer_context(self):
        """Agregar contexto adicional al serializer."""
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def handle_exception(self, exc):
        """Manejo centralizado de excepciones."""
        logger.error(f"Error en {self.__class__.__name__}: {str(exc)}")
        return super().handle_exception(exc)

    def perform_create(self, serializer):
        """Método común para la creación de objetos."""
        with transaction.atomic():
            instance = serializer.save()
            logger.info(
                f"Objeto {instance.__class__.__name__} creado por usuario {self.request.user.login}"
            )

    def perform_update(self, serializer):
        """Método común para la actualización de objetos."""
        with transaction.atomic():
            instance = serializer.save()
            logger.info(
                f"Objeto {instance.__class__.__name__} actualizado por usuario {self.request.user.login}"
            )

    def perform_destroy(self, instance):
        """Método común para la eliminación de objetos."""
        model_name = instance.__class__.__name__
        instance_id = instance.pk
        with transaction.atomic():
            instance.delete()
            logger.info(
                f"Objeto {model_name} (ID: {instance_id}) eliminado por usuario {self.request.user.login}"
            )


class EstadosViewSet(BaseViewSet):
    """
    ViewSet para gestionar los estados del sistema.
    """
    queryset = Estados.objects.filter(activo=True)
    serializer_class = EstadosSerializer
    search_fields = ['nombre_estado', 'descripcion']
    ordering_fields = ['nombre_estado', 'fecha_creacion']
    ordering = ['nombre_estado']

    @swagger_auto_schema(
        operation_description="Obtener todos los estados activos del sistema",
        responses={200: EstadosSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def inactivos(self, request):
        """Endpoint para obtener estados inactivos."""
        queryset = Estados.objects.filter(activo=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AreaViewSet(BaseViewSet):
    """
    ViewSet para gestionar las áreas departamentales.
    """
    queryset = Area.objects.select_related('estado', 'responsable').all()
    serializer_class = AreaSerializer
    search_fields = ['nombre_area', 'descripcion_area']
    ordering_fields = ['nombre_area', 'fecha_creacion']
    ordering = ['nombre_area']

    def get_queryset(self):
        """Optimizar consultas con select_related."""
        return Area.objects.select_related(
            'estado', 
            'responsable__cargo'
        ).prefetch_related(
            Prefetch('empleados', queryset=Empleados.objects.filter(is_active=True))
        )

    @action(detail=True, methods=['get'])
    def empleados(self, request, pk=None):
        """Obtener empleados de un área específica."""
        area = self.get_object()
        empleados = area.empleados.filter(is_active=True)
        serializer = EmpleadosSerializer(empleados, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Obtener estadísticas del área."""
        area = self.get_object()
        stats = {
            'total_empleados': area.empleados.filter(is_active=True).count(),
            'proyectos_activos': Proyecto.objects.filter(
                responsable__area=area,
                estado__nombre_estado__icontains='activo'
            ).count(),
            'tareas_pendientes': Tareas.objects.filter(
                asignado_a__area=area,
                completada=False
            ).count()
        }
        return Response(stats)


class CargoViewSet(BaseViewSet):
    """
    ViewSet para gestionar los cargos laborales.
    """
    queryset = Cargo.objects.filter(activo=True)
    serializer_class = CargoSerializer
    search_fields = ['nombre_cargo', 'descripcion']
    ordering_fields = ['nombre_cargo', 'nivel_jerarquico', 'salario_base']
    ordering = ['nivel_jerarquico', 'nombre_cargo']

    @action(detail=False, methods=['get'])
    def jerarquia(self, request):
        """Obtener cargos ordenados por jerarquía."""
        queryset = self.get_queryset().order_by('nivel_jerarquico')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EmpleadosViewSet(BaseViewSet):
    """
    ViewSet para gestionar los empleados del sistema.
    """
    queryset = Empleados.objects.select_related('cargo', 'estado', 'area').filter(is_active=True)
    serializer_class = EmpleadosSerializer
    search_fields = ['nombres', 'apellidos', 'correo_electronico', 'login']
    ordering_fields = ['nombres', 'apellidos', 'fecha_ingreso']
    ordering = ['apellidos', 'nombres']

    def get_queryset(self):
        """Optimizar consultas y filtros según el usuario."""
        queryset = Empleados.objects.select_related(
            'cargo', 'estado', 'area__estado'
        ).filter(is_active=True)
        
        # Si no es staff, solo puede ver empleados de su área
        if not self.request.user.is_staff:
            queryset = queryset.filter(area=self.request.user.area)
        
        return queryset

    @swagger_auto_schema(
        operation_description="Crear un nuevo empleado",
        request_body=EmpleadosSerializer,
        responses={
            201: EmpleadosSerializer,
            400: "Datos inválidos"
        }
    )
    def create(self, request, *args, **kwargs):
        """Crear empleado con validaciones adicionales."""
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                
                # Crear token de autenticación automáticamente
                empleado = serializer.save()
                token, created = Token.objects.get_or_create(user=empleado)
                
                response_data = serializer.data
                response_data['token'] = token.key
                
                logger.info(f"Empleado {empleado.login} creado exitosamente")
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creando empleado: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_update(self, serializer):
        """Actualizar empleado con encriptación de contraseña."""
        contrasena = serializer.validated_data.get('password')
        if contrasena:
            serializer.validated_data['password'] = make_password(contrasena)
        super().perform_update(serializer)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar el estado de un empleado."""
        empleado = self.get_object()
        nuevo_estado_id = request.data.get('estado_id')
        
        try:
            nuevo_estado = Estados.objects.get(id_estados=nuevo_estado_id)
            empleado.estado = nuevo_estado
            empleado.save()
            
            return Response({
                'message': f'Estado del empleado cambiado a {nuevo_estado.nombre_estado}'
            })
        except Estados.DoesNotExist:
            return Response(
                {'error': 'Estado no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def proyectos(self, request, pk=None):
        """Obtener proyectos asignados a un empleado."""
        empleado = self.get_object()
        proyectos = Proyecto.objects.filter(
            empleados_asignados__empleado=empleado,
            empleados_asignados__activo=True
        ).select_related('estado', 'prioridad')
        
        serializer = ProyectoSerializer(proyectos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tareas(self, request, pk=None):
        """Obtener tareas asignadas a un empleado."""
        empleado = self.get_object()
        tareas = empleado.tareas_asignadas.select_related(
            'proyecto', 'prioridad', 'estado'
        ).filter(completada=False)
        
        serializer = TareasSerializer(tareas, many=True)
        return Response(serializer.data)


class PrioridadViewSet(BaseViewSet):
    """
    ViewSet para gestionar las prioridades del sistema.
    """
    queryset = Prioridad.objects.filter(activo=True)
    serializer_class = PrioridadSerializer
    search_fields = ['nombre_prioridad']
    ordering_fields = ['nivel', 'nombre_prioridad']
    ordering = ['nivel']


class ProyectoViewSet(BaseViewSet):
    """
    ViewSet para gestionar los proyectos.
    """
    queryset = Proyecto.objects.select_related('estado', 'prioridad', 'responsable').all()
    serializer_class = ProyectoSerializer
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_inicio', 'fecha_fin_estimada', 'prioridad__nivel']
    ordering = ['-fecha_creacion']

    def get_queryset(self):
        """Optimizar consultas y filtros."""
        queryset = Proyecto.objects.select_related(
            'estado', 'prioridad', 'responsable__area'
        ).prefetch_related(
            'tareas__asignado_a',
            'empleados_asignados__empleado'
        )
        
        # Filtros opcionales
        estado = self.request.query_params.get('estado', None)
        prioridad = self.request.query_params.get('prioridad', None)
        
        if estado:
            queryset = queryset.filter(estado__nombre_estado__icontains=estado)
        if prioridad:
            queryset = queryset.filter(prioridad__nivel=prioridad)
            
        return queryset

    @action(detail=True, methods=['get'])
    def tareas(self, request, pk=None):
        """Obtener todas las tareas de un proyecto."""
        proyecto = self.get_object()
        tareas = proyecto.tareas.select_related(
            'asignado_a', 'prioridad', 'estado'
        ).prefetch_related('subtareas')
        
        serializer = TareasSerializer(tareas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def progreso(self, request, pk=None):
        """Obtener el progreso del proyecto."""
        proyecto = self.get_object()
        total_tareas = proyecto.tareas.count()
        tareas_completadas = proyecto.tareas.filter(completada=True).count()
        
        progreso = {
            'total_tareas': total_tareas,
            'tareas_completadas': tareas_completadas,
            'porcentaje_completado': (tareas_completadas / total_tareas * 100) if total_tareas > 0 else 0,
            'progreso_temporal': proyecto.progreso_temporal,
            'fecha_fin_estimada': proyecto.fecha_fin_estimada,
            'fecha_fin_real': proyecto.fecha_fin_real,
        }
        
        return Response(progreso)

    @action(detail=True, methods=['post'])
    def asignar_empleado(self, request, pk=None):
        """Asignar un empleado al proyecto."""
        proyecto = self.get_object()
        empleado_id = request.data.get('empleado_id')
        rol = request.data.get('rol', '')
        
        try:
            empleado = Empleados.objects.get(id_empleado=empleado_id)
            
            # Verificar si ya está asignado
            if EmpleadosProyecto.objects.filter(
                empleado=empleado, proyecto=proyecto, activo=True
            ).exists():
                return Response(
                    {'error': 'El empleado ya está asignado a este proyecto'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear asignación
            asignacion = EmpleadosProyecto.objects.create(
                empleado=empleado,
                proyecto=proyecto,
                rol_en_proyecto=rol
            )
            
            serializer = EmpleadosProyectoSerializer(asignacion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Empleados.DoesNotExist:
            return Response(
                {'error': 'Empleado no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class TareasViewSet(BaseViewSet):
    """
    ViewSet para gestionar las tareas.
    """
    queryset = Tareas.objects.select_related('proyecto', 'prioridad', 'asignado_a', 'estado').all()
    serializer_class = TareasSerializer
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_inicio', 'fecha_fin_estimada', 'prioridad__nivel']
    ordering = ['prioridad__nivel', 'fecha_fin_estimada']

    def get_queryset(self):
        """Filtrar tareas según el usuario."""
        queryset = Tareas.objects.select_related(
            'proyecto', 'prioridad', 'asignado_a', 'estado'
        ).prefetch_related('subtareas')
        
        # Si no es staff, solo puede ver sus tareas
        if not self.request.user.is_staff:
            queryset = queryset.filter(asignado_a=self.request.user)
        
        # Filtros adicionales
        proyecto = self.request.query_params.get('proyecto', None)
        completada = self.request.query_params.get('completada', None)
        
        if proyecto:
            queryset = queryset.filter(proyecto__id_proyecto=proyecto)
        if completada is not None:
            queryset = queryset.filter(completada=completada.lower() == 'true')
            
        return queryset

    @action(detail=True, methods=['post'])
    def marcar_completada(self, request, pk=None):
        """Marcar una tarea como completada."""
        tarea = self.get_object()
        
        with transaction.atomic():
            tarea.completada = True
            tarea.fecha_fin_real = timezone.now()
            tarea.save()
            
            # Registrar duración real si se proporciona
            duracion_real = request.data.get('duracion_real')
            if duracion_real:
                tarea.duracion_real = duracion_real
                tarea.save()
        
        return Response({'message': 'Tarea marcada como completada'})

    @action(detail=True, methods=['get'])
    def subtareas(self, request, pk=None):
        """Obtener subtareas de una tarea."""
        tarea = self.get_object()
        subtareas = tarea.subtareas.select_related('asignado_a')
        serializer = SubtareaSerializer(subtareas, many=True)
        return Response(serializer.data)


class SubtareaViewSet(BaseViewSet):
    """
    ViewSet para gestionar las subtareas.
    """
    queryset = Subtarea.objects.select_related('tarea', 'asignado_a').all()
    serializer_class = SubtareaSerializer
    search_fields = ['nombre_subtarea', 'descripcion']
    ordering_fields = ['nombre_subtarea', 'fecha_inicio', 'fecha_fin_estimada']
    ordering = ['tarea', 'fecha_inicio']

    def get_queryset(self):
        """Filtrar subtareas según el usuario."""
        queryset = Subtarea.objects.select_related('tarea__proyecto', 'asignado_a')
        
        # Si no es staff, solo puede ver sus subtareas
        if not self.request.user.is_staff:
            queryset = queryset.filter(asignado_a=self.request.user)
            
        return queryset

    @action(detail=True, methods=['post'])
    def marcar_completada(self, request, pk=None):
        """Marcar una subtarea como completada."""
        subtarea = self.get_object()
        
        with transaction.atomic():
            subtarea.completada = True
            subtarea.fecha_fin_real = timezone.now()
            
            # Registrar duración real si se proporciona
            duracion_real = request.data.get('duracion_real')
            if duracion_real:
                subtarea.duracion_real = duracion_real
                
            subtarea.save()
        
        return Response({'message': 'Subtarea marcada como completada'})


class LoginView(APIView):
    """
    Vista para autenticación de empleados.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Autenticar empleado en el sistema",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login exitoso",
                examples={
                    'application/json': {
                        'message': 'Login exitoso',
                        'token': 'auth-token',
                        'user': {
                            'id': 1,
                            'login': 'usuario',
                            'nombres': 'Juan',
                            'apellidos': 'Pérez'
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="Credenciales inválidas",
                examples={
                    'application/json': {
                        'error': 'Credenciales inválidas'
                    }
                }
            )
        }
    )
    def post(self, request):
        """Autenticar empleado y generar token."""
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Datos de entrada inválidos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        login_username = serializer.validated_data['login']
        contrasena = serializer.validated_data['contrasena']
        
        # Autenticar usuario
        user = authenticate(request, username=login_username, password=contrasena)
        
        if user is not None and user.is_active:
            auth_login(request, user)
            
            # Obtener o crear token
            token, created = Token.objects.get_or_create(user=user)
            
            logger.info(f"Login exitoso para usuario: {user.login}")
            
            return Response({
                'message': 'Login exitoso',
                'token': token.key,
                'user': {
                    'id': user.id_empleado,
                    'login': user.login,
                    'nombres': user.nombres,
                    'apellidos': user.apellidos,
                    'area': user.area.nombre_area,
                    'cargo': user.cargo.nombre_cargo
                }
            }, status=status.HTTP_200_OK)
        
        logger.warning(f"Intento de login fallido para usuario: {login_username}")
        return Response(
            {'error': 'Credenciales inválidas'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """
    Vista para cerrar sesión de empleados.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cerrar sesión del empleado",
        responses={
            200: openapi.Response(
                description="Logout exitoso",
                examples={
                    'application/json': {
                        'message': 'Logout exitoso'
                    }
                }
            )
        }
    )
    def post(self, request):
        """Cerrar sesión y eliminar token."""
        try:
            # Eliminar token de autenticación
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
            
            # Cerrar sesión
            logout(request)
            
            logger.info(f"Logout exitoso para usuario: {request.user.login}")
            
            return Response(
                {'message': 'Logout exitoso'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error en logout: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
