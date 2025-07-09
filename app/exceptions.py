"""
Manejo de excepciones personalizado para el sistema Aurora.

Este módulo contiene:
- Manejador personalizado de excepciones para DRF
- Excepciones personalizadas para el negocio
- Logging de errores
- Formateo consistente de respuestas de error

Autor: Equipo de Desarrollo Aurora
Fecha: 2024
"""

import logging
import sys
import traceback
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.http import Http404
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError, AuthenticationFailed, PermissionDenied as DRFPermissionDenied,
    NotFound, MethodNotAllowed, ParseError, Throttled
)

# Configurar logger
logger = logging.getLogger(__name__)


class AuroraException(Exception):
    """
    Excepción base para todas las excepciones personalizadas del sistema Aurora.
    """
    default_message = "Ha ocurrido un error en el sistema Aurora"
    default_code = "aurora_error"
    
    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)


class EmpleadoNotFoundError(AuroraException):
    """
    Excepción cuando no se encuentra un empleado.
    """
    default_message = "Empleado no encontrado"
    default_code = "empleado_not_found"


class ProyectoNotFoundError(AuroraException):
    """
    Excepción cuando no se encuentra un proyecto.
    """
    default_message = "Proyecto no encontrado"
    default_code = "proyecto_not_found"


class TareaNotFoundError(AuroraException):
    """
    Excepción cuando no se encuentra una tarea.
    """
    default_message = "Tarea no encontrada"
    default_code = "tarea_not_found"


class AsignacionDuplicadaError(AuroraException):
    """
    Excepción cuando se intenta crear una asignación duplicada.
    """
    default_message = "El empleado ya está asignado a este proyecto"
    default_code = "asignacion_duplicada"


class EstadoInvalidoError(AuroraException):
    """
    Excepción cuando se intenta usar un estado inválido.
    """
    default_message = "Estado inválido para esta operación"
    default_code = "estado_invalido"


class CredencialesInvalidasError(AuroraException):
    """
    Excepción para credenciales inválidas.
    """
    default_message = "Las credenciales proporcionadas son inválidas"
    default_code = "credenciales_invalidas"


class PermisosDenegadosError(AuroraException):
    """
    Excepción cuando el usuario no tiene permisos para una operación.
    """
    default_message = "No tiene permisos para realizar esta operación"
    default_code = "permisos_denegados"


class FechaInvalidaError(AuroraException):
    """
    Excepción para fechas inválidas.
    """
    default_message = "La fecha proporcionada es inválida"
    default_code = "fecha_invalida"


class OperacionNoPermitidaError(AuroraException):
    """
    Excepción cuando una operación no está permitida en el estado actual.
    """
    default_message = "Operación no permitida en el estado actual"
    default_code = "operacion_no_permitida"


def get_error_details(exc, context=None):
    """
    Extraer detalles específicos del error según el tipo de excepción.
    """
    details = {}
    
    if isinstance(exc, ValidationError):
        details['validation_errors'] = exc.detail
    elif isinstance(exc, IntegrityError):
        details['database_error'] = str(exc)
    elif isinstance(exc, AuroraException):
        details.update(exc.details)
    
    # Agregar información del contexto si está disponible
    if context:
        view = context.get('view')
        request = context.get('request')
        
        if view:
            details['view'] = view.__class__.__name__
            details['action'] = getattr(view, 'action', None)
        
        if request:
            details['method'] = request.method
            details['path'] = request.path
            details['user'] = str(request.user) if hasattr(request, 'user') else 'Anonymous'
    
    return details


def get_status_code(exc):
    """
    Determinar el código de estado HTTP apropiado para la excepción.
    """
    if isinstance(exc, (Http404, NotFound)):
        return status.HTTP_404_NOT_FOUND
    elif isinstance(exc, (PermissionDenied, DRFPermissionDenied, PermisosDenegadosError)):
        return status.HTTP_403_FORBIDDEN
    elif isinstance(exc, (AuthenticationFailed, CredencialesInvalidasError)):
        return status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, ValidationError):
        return status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, MethodNotAllowed):
        return status.HTTP_405_METHOD_NOT_ALLOWED
    elif isinstance(exc, ParseError):
        return status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, Throttled):
        return status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exc, IntegrityError):
        return status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, AuroraException):
        # Mapear excepciones personalizadas a códigos HTTP
        error_code_mapping = {
            'empleado_not_found': status.HTTP_404_NOT_FOUND,
            'proyecto_not_found': status.HTTP_404_NOT_FOUND,
            'tarea_not_found': status.HTTP_404_NOT_FOUND,
            'asignacion_duplicada': status.HTTP_400_BAD_REQUEST,
            'estado_invalido': status.HTTP_400_BAD_REQUEST,
            'credenciales_invalidas': status.HTTP_401_UNAUTHORIZED,
            'permisos_denegados': status.HTTP_403_FORBIDDEN,
            'fecha_invalida': status.HTTP_400_BAD_REQUEST,
            'operacion_no_permitida': status.HTTP_400_BAD_REQUEST,
        }
        return error_code_mapping.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR


def get_error_message(exc):
    """
    Obtener el mensaje de error apropiado.
    """
    if isinstance(exc, ValidationError):
        if isinstance(exc.detail, dict):
            # Flatten validation errors
            messages = []
            for field, errors in exc.detail.items():
                if isinstance(errors, list):
                    messages.extend([f"{field}: {error}" for error in errors])
                else:
                    messages.append(f"{field}: {errors}")
            return "; ".join(messages)
        elif isinstance(exc.detail, list):
            return "; ".join(str(error) for error in exc.detail)
        else:
            return str(exc.detail)
    elif isinstance(exc, AuroraException):
        return exc.message
    elif isinstance(exc, IntegrityError):
        # Intentar extraer información útil del error de integridad
        error_str = str(exc)
        if 'UNIQUE constraint failed' in error_str:
            return "Ya existe un registro con estos datos únicos"
        elif 'FOREIGN KEY constraint failed' in error_str:
            return "Referencia a un registro que no existe"
        else:
            return "Error de integridad en la base de datos"
    else:
        return str(exc)


def log_exception(exc, context=None, level=logging.ERROR):
    """
    Registrar la excepción en los logs con información contextual.
    """
    details = get_error_details(exc, context)
    
    # Preparar información adicional para el log
    log_data = {
        'exception_type': exc.__class__.__name__,
        'message': str(exc),
        'details': details
    }
    
    # Agregar traceback para errores 500
    if get_status_code(exc) == status.HTTP_500_INTERNAL_SERVER_ERROR:
        log_data['traceback'] = traceback.format_exc()
    
    logger.log(level, f"Exception occurred: {exc.__class__.__name__}", extra=log_data)


def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones para Django REST Framework.
    
    Proporciona respuestas consistentes y logging detallado de errores.
    """
    # Llamar al manejador por defecto de DRF primero
    response = exception_handler(exc, context)
    
    # Si DRF no manejó la excepción, la manejamos nosotros
    if response is None:
        status_code = get_status_code(exc)
        
        # Preparar respuesta personalizada
        custom_response_data = {
            'error': True,
            'status_code': status_code,
            'message': get_error_message(exc),
            'code': getattr(exc, 'code', 'internal_error'),
            'timestamp': None,
            'path': context.get('request').path if context else None
        }
        
        # Agregar timestamp
        from django.utils import timezone
        custom_response_data['timestamp'] = timezone.now().isoformat()
        
        # Agregar detalles en modo debug
        from django.conf import settings
        if settings.DEBUG:
            custom_response_data['details'] = get_error_details(exc, context)
            if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                custom_response_data['traceback'] = traceback.format_exc()
        
        response = Response(custom_response_data, status=status_code)
    
    else:
        # Modificar la respuesta de DRF para que sea consistente
        if hasattr(response, 'data'):
            status_code = response.status_code
            
            # Estructura consistente para todas las respuestas de error
            if isinstance(response.data, dict):
                error_data = {
                    'error': True,
                    'status_code': status_code,
                    'message': get_error_message(exc),
                    'code': getattr(exc, 'code', 'validation_error'),
                    'timestamp': None,
                    'path': context.get('request').path if context else None
                }
                
                # Agregar timestamp
                from django.utils import timezone
                error_data['timestamp'] = timezone.now().isoformat()
                
                # Preservar detalles de validación
                if 'detail' in response.data:
                    error_data['validation_errors'] = response.data
                elif response.data:
                    error_data['validation_errors'] = response.data
                
                # Agregar detalles adicionales en modo debug
                from django.conf import settings
                if settings.DEBUG:
                    error_data['details'] = get_error_details(exc, context)
                
                response.data = error_data
    
    # Registrar la excepción
    log_level = logging.WARNING if response.status_code < 500 else logging.ERROR
    log_exception(exc, context, log_level)
    
    # Agregar headers personalizados
    if response:
        response['X-Aurora-Error'] = 'true'
        response['X-Aurora-Error-Code'] = getattr(exc, 'code', 'unknown')
    
    return response


def handle_business_logic_error(func):
    """
    Decorador para manejar errores de lógica de negocio.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuroraException:
            # Re-raise excepciones personalizadas
            raise
        except DjangoValidationError as e:
            # Convertir excepciones de validación de Django
            raise ValidationError(str(e))
        except IntegrityError as e:
            # Manejar errores de integridad de base de datos
            logger.error(f"Database integrity error in {func.__name__}: {str(e)}")
            raise ValidationError("Error de integridad en los datos")
        except Exception as e:
            # Manejar errores inesperados
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise AuroraException(
                message="Ha ocurrido un error inesperado",
                code="unexpected_error",
                details={'original_error': str(e)}
            )
    
    return wrapper