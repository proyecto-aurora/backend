"""
Señales de Django para el sistema Aurora.

Este módulo contiene todas las señales (signals) que se ejecutan automáticamente
en respuesta a eventos del sistema como creación, actualización o eliminación
de modelos.

Autor: Equipo de Desarrollo Aurora
Fecha: 2024
"""

import logging
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from rest_framework.authtoken.models import Token

from .models import (
    Empleados, Proyecto, Tareas, Subtarea, Area, 
    Estados, EmpleadosProyecto
)

# Configurar logger
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Empleados)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Crear token de autenticación automáticamente cuando se crea un empleado.
    """
    if created:
        try:
            Token.objects.create(user=instance)
            logger.info(f"Token de autenticación creado para empleado: {instance.login}")
        except Exception as e:
            logger.error(f"Error creando token para empleado {instance.login}: {str(e)}")


@receiver(pre_save, sender=Empleados)
def validate_empleado_before_save(sender, instance, **kwargs):
    """
    Validaciones adicionales antes de guardar un empleado.
    """
    # Normalizar datos
    if instance.nombres:
        instance.nombres = instance.nombres.strip().title()
    if instance.apellidos:
        instance.apellidos = instance.apellidos.strip().title()
    if instance.login:
        instance.login = instance.login.strip().lower()
    
    # Log de la operación
    if instance.pk:
        logger.info(f"Actualizando empleado: {instance.login}")
    else:
        logger.info(f"Creando nuevo empleado: {instance.login}")


@receiver(post_save, sender=Proyecto)
def handle_proyecto_creation(sender, instance=None, created=False, **kwargs):
    """
    Manejar eventos al crear o actualizar un proyecto.
    """
    if created:
        logger.info(f"Proyecto creado: {instance.nombre} por {instance.responsable}")
        
        # Asignar automáticamente al responsable del proyecto
        try:
            EmpleadosProyecto.objects.get_or_create(
                empleado=instance.responsable,
                proyecto=instance,
                defaults={
                    'rol_en_proyecto': 'Responsable del Proyecto',
                    'activo': True
                }
            )
            logger.info(f"Responsable {instance.responsable} asignado automáticamente al proyecto {instance.nombre}")
        except Exception as e:
            logger.error(f"Error asignando responsable al proyecto: {str(e)}")
    else:
        logger.info(f"Proyecto actualizado: {instance.nombre}")


@receiver(post_save, sender=Tareas)
def handle_tarea_completion(sender, instance=None, created=False, **kwargs):
    """
    Manejar eventos cuando una tarea es marcada como completada.
    """
    if not created and instance.completada:
        # Si la tarea se marca como completada, establecer fecha de finalización
        if not instance.fecha_fin_real:
            instance.fecha_fin_real = timezone.now()
            # Evitar recursión usando update en lugar de save
            Tareas.objects.filter(pk=instance.pk).update(fecha_fin_real=instance.fecha_fin_real)
            
        logger.info(f"Tarea completada: {instance.nombre} por {instance.asignado_a}")
        
        # Verificar si todas las tareas del proyecto están completadas
        proyecto = instance.proyecto
        tareas_pendientes = proyecto.tareas.filter(completada=False)
        
        if not tareas_pendientes.exists():
            logger.info(f"Todas las tareas del proyecto {proyecto.nombre} han sido completadas")


@receiver(post_save, sender=Subtarea)
def handle_subtarea_completion(sender, instance=None, created=False, **kwargs):
    """
    Manejar eventos cuando una subtarea es completada.
    """
    if not created and instance.completada:
        # Si la subtarea se marca como completada, establecer fecha de finalización
        if not instance.fecha_fin_real:
            instance.fecha_fin_real = timezone.now()
            # Evitar recursión usando update
            Subtarea.objects.filter(pk=instance.pk).update(fecha_fin_real=instance.fecha_fin_real)
            
        logger.info(f"Subtarea completada: {instance.nombre_subtarea} por {instance.asignado_a}")
        
        # Verificar si todas las subtareas de la tarea están completadas
        tarea = instance.tarea
        subtareas_pendientes = tarea.subtareas.filter(completada=False)
        
        if not subtareas_pendientes.exists() and not tarea.completada:
            logger.info(f"Todas las subtareas de la tarea {tarea.nombre} han sido completadas")


@receiver(pre_delete, sender=Empleados)
def handle_empleado_deletion(sender, instance, **kwargs):
    """
    Manejar la eliminación de empleados.
    """
    logger.warning(f"Eliminando empleado: {instance.nombre_completo} ({instance.login})")
    
    # Verificar si el empleado tiene proyectos asignados
    proyectos_asignados = instance.proyectos_asignados.filter(activo=True).count()
    if proyectos_asignados > 0:
        logger.warning(f"Empleado {instance.login} tiene {proyectos_asignados} proyectos asignados")
    
    # Verificar si el empleado tiene tareas pendientes
    tareas_pendientes = instance.tareas_asignadas.filter(completada=False).count()
    if tareas_pendientes > 0:
        logger.warning(f"Empleado {instance.login} tiene {tareas_pendientes} tareas pendientes")


@receiver(pre_delete, sender=Proyecto)
def handle_proyecto_deletion(sender, instance, **kwargs):
    """
    Manejar la eliminación de proyectos.
    """
    logger.warning(f"Eliminando proyecto: {instance.nombre}")
    
    # Contar tareas asociadas
    tareas_count = instance.tareas.count()
    if tareas_count > 0:
        logger.warning(f"Proyecto {instance.nombre} tiene {tareas_count} tareas que serán eliminadas")


@receiver(post_save, sender=Area)
def handle_area_updates(sender, instance=None, created=False, **kwargs):
    """
    Manejar eventos de áreas.
    """
    if created:
        logger.info(f"Área creada: {instance.nombre_area}")
    else:
        logger.info(f"Área actualizada: {instance.nombre_area}")


@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    """
    Manejar eventos de login de usuarios.
    """
    if hasattr(user, 'login'):
        logger.info(f"Usuario logueado: {user.login} desde IP: {get_client_ip(request)}")
    else:
        logger.info(f"Usuario logueado: {user.username} desde IP: {get_client_ip(request)}")


@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    """
    Manejar eventos de logout de usuarios.
    """
    if user and hasattr(user, 'login'):
        logger.info(f"Usuario deslogueado: {user.login}")
    elif user:
        logger.info(f"Usuario deslogueado: {user.username}")


def get_client_ip(request):
    """
    Obtener la IP del cliente desde el request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(post_save, sender=EmpleadosProyecto)
def handle_empleado_proyecto_assignment(sender, instance=None, created=False, **kwargs):
    """
    Manejar asignaciones de empleados a proyectos.
    """
    if created:
        logger.info(
            f"Empleado {instance.empleado.nombre_completo} asignado al proyecto "
            f"{instance.proyecto.nombre} con rol: {instance.rol_en_proyecto or 'Sin rol especificado'}"
        )
    elif not instance.activo:
        logger.info(
            f"Empleado {instance.empleado.nombre_completo} desasignado del proyecto {instance.proyecto.nombre}"
        )