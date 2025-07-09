"""
Configuración de la aplicación Aurora.

Este módulo contiene la configuración principal de la aplicación Django,
incluyendo configuraciones de inicialización, señales y metadatos.

Autor: Equipo de Desarrollo Aurora
Fecha: 2024
"""

import logging
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management.color import no_style
from django.db import connection

logger = logging.getLogger(__name__)


class AppConfig(AppConfig):
    """
    Configuración principal de la aplicación Aurora.
    
    Esta clase maneja:
    - Configuración de campos por defecto
    - Inicialización de la aplicación
    - Configuración de señales
    - Creación de datos iniciales
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = 'Sistema Aurora - Gestión de Empleados y Proyectos'
    
    def ready(self):
        """
        Método llamado cuando la aplicación está lista.
        Aquí se configuran señales y inicializaciones.
        """
        # Importar señales para que se registren
        try:
            from . import signals
            logger.info("Señales de la aplicación Aurora cargadas exitosamente")
        except ImportError:
            logger.warning("No se encontró el módulo de señales")
        
        # Configurar logging específico de la aplicación
        self.setup_logging()
        
        # Conectar señal post_migrate para crear datos iniciales
        post_migrate.connect(self.create_initial_data, sender=self)
        
        logger.info(f"Aplicación {self.verbose_name} inicializada correctamente")
    
    def setup_logging(self):
        """
        Configurar logging específico para la aplicación.
        """
        try:
            # Configuración adicional de logging si es necesario
            app_logger = logging.getLogger('app')
            if not app_logger.handlers:
                logger.info("Configurando logging para la aplicación Aurora")
        except Exception as e:
            logger.error(f"Error configurando logging: {e}")
    
    def create_initial_data(self, sender, **kwargs):
        """
        Crear datos iniciales después de las migraciones.
        """
        if sender.name != self.name:
            return
        
        try:
            logger.info("Verificando datos iniciales de Aurora...")
            
            # Importar modelos localmente para evitar problemas de importación
            from .models import Estados, Prioridad, Cargo
            
            # Crear estados iniciales si no existen
            self._create_initial_estados()
            
            # Crear prioridades iniciales si no existen
            self._create_initial_prioridades()
            
            # Crear cargos iniciales si no existen
            self._create_initial_cargos()
            
            logger.info("Datos iniciales de Aurora verificados/creados exitosamente")
            
        except Exception as e:
            logger.error(f"Error creando datos iniciales: {e}")
    
    def _create_initial_estados(self):
        """
        Crear estados iniciales del sistema.
        """
        from .models import Estados
        
        estados_iniciales = [
            {'nombre_estado': 'Activo', 'descripcion': 'Estado activo para entidades del sistema'},
            {'nombre_estado': 'Inactivo', 'descripcion': 'Estado inactivo para entidades del sistema'},
            {'nombre_estado': 'En Progreso', 'descripcion': 'Para proyectos y tareas en desarrollo'},
            {'nombre_estado': 'Completado', 'descripcion': 'Para proyectos y tareas finalizadas'},
            {'nombre_estado': 'Pausado', 'descripcion': 'Para proyectos y tareas temporalmente detenidas'},
            {'nombre_estado': 'Cancelado', 'descripcion': 'Para proyectos y tareas canceladas'},
        ]
        
        created_count = 0
        for estado_data in estados_iniciales:
            estado, created = Estados.objects.get_or_create(
                nombre_estado=estado_data['nombre_estado'],
                defaults=estado_data
            )
            if created:
                created_count += 1
        
        if created_count > 0:
            logger.info(f"Creados {created_count} estados iniciales")
    
    def _create_initial_prioridades(self):
        """
        Crear prioridades iniciales del sistema.
        """
        from .models import Prioridad
        
        prioridades_iniciales = [
            {'nombre_prioridad': 'Crítica', 'nivel': 1, 'color': '#FF0000'},
            {'nombre_prioridad': 'Alta', 'nivel': 2, 'color': '#FF8000'},
            {'nombre_prioridad': 'Media', 'nivel': 3, 'color': '#FFFF00'},
            {'nombre_prioridad': 'Baja', 'nivel': 4, 'color': '#00FF00'},
            {'nombre_prioridad': 'Muy Baja', 'nivel': 5, 'color': '#0080FF'},
        ]
        
        created_count = 0
        for prioridad_data in prioridades_iniciales:
            prioridad, created = Prioridad.objects.get_or_create(
                nombre_prioridad=prioridad_data['nombre_prioridad'],
                defaults=prioridad_data
            )
            if created:
                created_count += 1
        
        if created_count > 0:
            logger.info(f"Creadas {created_count} prioridades iniciales")
    
    def _create_initial_cargos(self):
        """
        Crear cargos iniciales del sistema.
        """
        from .models import Cargo
        
        cargos_iniciales = [
            {
                'nombre_cargo': 'Administrador del Sistema',
                'descripcion': 'Administrador general del sistema Aurora',
                'nivel_jerarquico': 1,
                'salario_base': 5000000.00
            },
            {
                'nombre_cargo': 'Gerente de Proyecto',
                'descripcion': 'Responsable de la gestión de proyectos',
                'nivel_jerarquico': 2,
                'salario_base': 4000000.00
            },
            {
                'nombre_cargo': 'Líder de Equipo',
                'descripcion': 'Líder de equipos de trabajo',
                'nivel_jerarquico': 3,
                'salario_base': 3500000.00
            },
            {
                'nombre_cargo': 'Desarrollador Senior',
                'descripcion': 'Desarrollador con experiencia avanzada',
                'nivel_jerarquico': 4,
                'salario_base': 3000000.00
            },
            {
                'nombre_cargo': 'Desarrollador',
                'descripcion': 'Desarrollador de software',
                'nivel_jerarquico': 5,
                'salario_base': 2500000.00
            },
            {
                'nombre_cargo': 'Desarrollador Junior',
                'descripcion': 'Desarrollador en formación',
                'nivel_jerarquico': 6,
                'salario_base': 2000000.00
            },
            {
                'nombre_cargo': 'Analista',
                'descripcion': 'Analista de sistemas y procesos',
                'nivel_jerarquico': 5,
                'salario_base': 2300000.00
            },
            {
                'nombre_cargo': 'Tester',
                'descripcion': 'Especialista en pruebas de software',
                'nivel_jerarquico': 5,
                'salario_base': 2200000.00
            },
        ]
        
        created_count = 0
        for cargo_data in cargos_iniciales:
            cargo, created = Cargo.objects.get_or_create(
                nombre_cargo=cargo_data['nombre_cargo'],
                defaults=cargo_data
            )
            if created:
                created_count += 1
        
        if created_count > 0:
            logger.info(f"Creados {created_count} cargos iniciales")
    
    @staticmethod
    def get_version():
        """
        Obtener la versión de la aplicación.
        """
        return "1.0.0"
    
    @staticmethod
    def get_app_info():
        """
        Obtener información completa de la aplicación.
        """
        return {
            'name': 'Aurora',
            'version': AppConfig.get_version(),
            'description': 'Sistema de gestión de empleados, proyectos y tareas',
            'author': 'Equipo de Desarrollo Aurora',
            'django_app': 'app',
        }
