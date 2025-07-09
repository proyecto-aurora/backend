"""
Modelos de datos para el sistema Aurora.

Este módulo contiene todos los modelos de Django para la gestión de:
- Empleados y autenticación
- Áreas y cargos organizacionales  
- Proyectos, tareas y subtareas
- Estados y prioridades

Autor: Equipo de Desarrollo Aurora
Fecha: 2024
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinLengthValidator, RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
import uuid


class TimestampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de timestamp automáticos.
    """
    fecha_creacion = models.DateTimeField(
        'Fecha de Creación',
        default=timezone.now,
        help_text="Fecha y hora de creación del registro"
    )
    fecha_actualizacion = models.DateTimeField(
        'Fecha de Actualización',
        auto_now=True,
        help_text="Fecha y hora de última actualización"
    )

    class Meta:
        abstract = True


class Estados(TimestampedModel):
    """
    Modelo para gestionar los diferentes estados del sistema.
    """
    id_estados = models.AutoField(
        'ID Estado',
        primary_key=True
    )
    nombre_estado = models.CharField(
        'Nombre del Estado',
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="Nombre descriptivo del estado"
    )
    descripcion = models.TextField(
        'Descripción',
        blank=True,
        null=True,
        help_text="Descripción detallada del estado"
    )
    activo = models.BooleanField(
        'Activo',
        default=True,
        help_text="Indica si el estado está activo"
    )

    class Meta:
        db_table = 'estados'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        ordering = ['nombre_estado']

    def __str__(self):
        return self.nombre_estado

    def clean(self):
        """Validaciones personalizadas."""
        if self.nombre_estado:
            self.nombre_estado = self.nombre_estado.strip().title()


class Area(TimestampedModel):
    """
    Modelo para gestionar las áreas departamentales de la organización.
    """
    id_area = models.AutoField(
        'ID Área',
        primary_key=True
    )
    nombre_area = models.CharField(
        'Nombre del Área',
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="Nombre del área departamental"
    )
    descripcion_area = models.TextField(
        'Descripción del Área',
        blank=True,
        null=True,
        help_text="Descripción detallada del área"
    )
    estado = models.ForeignKey(
        Estados,
        on_delete=models.PROTECT,
        verbose_name='Estado',
        help_text="Estado actual del área"
    )
    responsable = models.ForeignKey(
        'Empleados',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='areas_responsable',
        verbose_name='Responsable del Área',
        help_text="Empleado responsable del área"
    )

    class Meta:
        db_table = 'area'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['nombre_area']

    def __str__(self):
        return self.nombre_area

    def clean(self):
        """Validaciones personalizadas."""
        if self.nombre_area:
            self.nombre_area = self.nombre_area.strip().title()


class Cargo(TimestampedModel):
    """
    Modelo para gestionar los cargos laborales.
    """
    id_cargo = models.AutoField(
        'ID Cargo',
        primary_key=True
    )
    nombre_cargo = models.CharField(
        'Nombre del Cargo',
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="Nombre del cargo laboral"
    )
    descripcion = models.TextField(
        'Descripción',
        blank=True,
        null=True,
        help_text="Descripción detallada del cargo"
    )
    nivel_jerarquico = models.PositiveIntegerField(
        'Nivel Jerárquico',
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Nivel jerárquico del cargo (1=más alto)"
    )
    salario_base = models.DecimalField(
        'Salario Base',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Salario base del cargo"
    )
    activo = models.BooleanField(
        'Activo',
        default=True,
        help_text="Indica si el cargo está activo"
    )

    class Meta:
        db_table = 'cargo'
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['nivel_jerarquico', 'nombre_cargo']

    def __str__(self):
        return self.nombre_cargo

    def clean(self):
        """Validaciones personalizadas."""
        if self.nombre_cargo:
            self.nombre_cargo = self.nombre_cargo.strip().title()


class EmpleadosManager(BaseUserManager):
    """
    Manager personalizado para el modelo de Empleados.
    """
    
    def create_user(self, login, contrasena=None, **extra_fields):
        """
        Crea y guarda un empleado regular con el login y contraseña dados.
        """
        if not login:
            raise ValueError('El campo login es obligatorio')
        
        # Normalizar email si existe
        if 'correo_electronico' in extra_fields:
            extra_fields['correo_electronico'] = self.normalize_email(
                extra_fields['correo_electronico']
            )
        
        user = self.model(login=login, **extra_fields)
        user.set_password(contrasena)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, contrasena, **extra_fields):
        """
        Crea y guarda un superusuario con el login y contraseña dados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(login, contrasena, **extra_fields)


class Empleados(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """
    Modelo personalizado de usuario para empleados del sistema.
    """
    
    # Validadores personalizados
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Número de teléfono debe tener entre 9 y 15 dígitos."
    )
    
    id_empleado = models.AutoField(
        'ID Empleado',
        primary_key=True
    )
    uuid = models.UUIDField(
        'UUID',
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Identificador único universal"
    )
    nombres = models.CharField(
        'Nombres',
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Nombres del empleado"
    )
    apellidos = models.CharField(
        'Apellidos',
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Apellidos del empleado"
    )
    correo_electronico = models.EmailField(
        'Correo Electrónico',
        unique=True,
        help_text="Dirección de correo electrónico"
    )
    celular = models.CharField(
        'Celular',
        max_length=20,
        unique=True,
        validators=[phone_validator],
        help_text="Número de celular"
    )
    login = models.CharField(
        'Usuario',
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(3),
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message="El login solo puede contener letras, números y guiones bajos."
            )
        ],
        help_text="Nombre de usuario para acceso al sistema"
    )
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.PROTECT,
        verbose_name='Cargo',
        help_text="Cargo del empleado"
    )
    estado = models.ForeignKey(
        Estados,
        on_delete=models.PROTECT,
        verbose_name='Estado',
        help_text="Estado actual del empleado"
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        verbose_name='Área',
        related_name='empleados',
        help_text="Área de trabajo del empleado"
    )
    fecha_ingreso = models.DateField(
        'Fecha de Ingreso',
        default=timezone.now,
        help_text="Fecha de ingreso a la empresa"
    )
    fecha_nacimiento = models.DateField(
        'Fecha de Nacimiento',
        null=True,
        blank=True,
        help_text="Fecha de nacimiento del empleado"
    )
    is_active = models.BooleanField(
        'Activo',
        default=True,
        help_text="Designa si este usuario debe ser tratado como activo"
    )
    is_staff = models.BooleanField(
        'Es Staff',
        default=False,
        help_text="Designa si el usuario puede acceder al sitio de administración"
    )

    objects = EmpleadosManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'correo_electronico']

    class Meta:
        db_table = 'empleados'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['apellidos', 'nombres']
        indexes = [
            models.Index(fields=['login']),
            models.Index(fields=['correo_electronico']),
            models.Index(fields=['area', 'cargo']),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def clean(self):
        """Validaciones personalizadas."""
        if self.nombres:
            self.nombres = self.nombres.strip().title()
        if self.apellidos:
            self.apellidos = self.apellidos.strip().title()
        if self.login:
            self.login = self.login.strip().lower()

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del empleado."""
        return f"{self.nombres} {self.apellidos}"

    @property
    def edad(self):
        """Calcula la edad del empleado."""
        if self.fecha_nacimiento:
            today = timezone.now().date()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None


class Prioridad(models.Model):
    """
    Modelo para gestionar las prioridades del sistema.
    """
    id_prioridad = models.AutoField(
        'ID Prioridad',
        primary_key=True
    )
    nombre_prioridad = models.CharField(
        'Nombre de la Prioridad',
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="Nombre de la prioridad"
    )
    nivel = models.PositiveIntegerField(
        'Nivel',
        unique=True,
        validators=[MinValueValidator(1)],
        help_text="Nivel numérico de prioridad (1=más alta)"
    )
    color = models.CharField(
        'Color',
        max_length=7,
        default='#000000',
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message="Debe ser un color hexadecimal válido."
            )
        ],
        help_text="Color hexadecimal para representar la prioridad"
    )
    activo = models.BooleanField(
        'Activo',
        default=True,
        help_text="Indica si la prioridad está activa"
    )

    class Meta:
        db_table = 'prioridad'
        verbose_name = 'Prioridad'
        verbose_name_plural = 'Prioridades'
        ordering = ['nivel']

    def __str__(self):
        return f"{self.nombre_prioridad} (Nivel {self.nivel})"

    def clean(self):
        """Validaciones personalizadas."""
        if self.nombre_prioridad:
            self.nombre_prioridad = self.nombre_prioridad.strip().title()


class Proyecto(TimestampedModel):
    """
    Modelo para gestionar los proyectos de la organización.
    """
    id_proyecto = models.AutoField(
        'ID Proyecto',
        primary_key=True
    )
    uuid = models.UUIDField(
        'UUID',
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    nombre = models.CharField(
        'Nombre del Proyecto',
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text="Nombre del proyecto"
    )
    descripcion = models.TextField(
        'Descripción',
        help_text="Descripción detallada del proyecto"
    )
    duracion_estimada = models.PositiveIntegerField(
        'Duración Estimada (días)',
        validators=[MinValueValidator(1)],
        help_text="Duración estimada en días"
    )
    fecha_inicio = models.DateField(
        'Fecha de Inicio',
        default=timezone.now,
        help_text="Fecha de inicio del proyecto"
    )
    fecha_fin_estimada = models.DateField(
        'Fecha de Fin Estimada',
        help_text="Fecha estimada de finalización"
    )
    fecha_fin_real = models.DateField(
        'Fecha de Fin Real',
        null=True,
        blank=True,
        help_text="Fecha real de finalización"
    )
    estado = models.ForeignKey(
        Estados,
        on_delete=models.PROTECT,
        verbose_name='Estado',
        help_text="Estado actual del proyecto"
    )
    prioridad = models.ForeignKey(
        Prioridad,
        on_delete=models.PROTECT,
        verbose_name='Prioridad',
        help_text="Prioridad del proyecto"
    )
    presupuesto = models.DecimalField(
        'Presupuesto',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Presupuesto asignado al proyecto"
    )
    responsable = models.ForeignKey(
        Empleados,
        on_delete=models.PROTECT,
        related_name='proyectos_responsable',
        verbose_name='Responsable',
        help_text="Empleado responsable del proyecto"
    )

    class Meta:
        db_table = 'proyecto'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['responsable']),
            models.Index(fields=['fecha_inicio', 'fecha_fin_estimada']),
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        """Validaciones personalizadas."""
        if self.fecha_fin_estimada and self.fecha_inicio:
            if self.fecha_fin_estimada <= self.fecha_inicio:
                raise ValidationError(
                    'La fecha de fin estimada debe ser posterior a la fecha de inicio.'
                )
        
        if self.fecha_fin_real and self.fecha_inicio:
            if self.fecha_fin_real < self.fecha_inicio:
                raise ValidationError(
                    'La fecha de fin real no puede ser anterior a la fecha de inicio.'
                )

    @property
    def progreso_temporal(self):
        """Calcula el progreso temporal del proyecto."""
        if not self.fecha_fin_estimada:
            return 0
        
        today = timezone.now().date()
        total_days = (self.fecha_fin_estimada - self.fecha_inicio).days
        elapsed_days = (today - self.fecha_inicio).days
        
        if total_days <= 0:
            return 100
        
        progress = (elapsed_days / total_days) * 100
        return max(0, min(100, progress))


class Tareas(TimestampedModel):
    """
    Modelo para gestionar las tareas de un proyecto.
    """
    id_tareas = models.AutoField(
        'ID Tarea',
        primary_key=True
    )
    uuid = models.UUIDField(
        'UUID',
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    nombre = models.CharField(
        'Nombre de la Tarea',
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text="Nombre de la tarea"
    )
    descripcion = models.TextField(
        'Descripción',
        help_text="Descripción detallada de la tarea"
    )
    duracion_estimada = models.PositiveIntegerField(
        'Duración Estimada (horas)',
        validators=[MinValueValidator(1)],
        help_text="Duración estimada en horas"
    )
    duracion_real = models.PositiveIntegerField(
        'Duración Real (horas)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Duración real en horas"
    )
    fecha_inicio = models.DateTimeField(
        'Fecha de Inicio',
        default=timezone.now,
        help_text="Fecha y hora de inicio de la tarea"
    )
    fecha_fin_estimada = models.DateTimeField(
        'Fecha de Fin Estimada',
        help_text="Fecha y hora estimada de finalización"
    )
    fecha_fin_real = models.DateTimeField(
        'Fecha de Fin Real',
        null=True,
        blank=True,
        help_text="Fecha y hora real de finalización"
    )
    prioridad = models.ForeignKey(
        Prioridad,
        on_delete=models.PROTECT,
        verbose_name='Prioridad',
        help_text="Prioridad de la tarea"
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='tareas',
        verbose_name='Proyecto',
        help_text="Proyecto al que pertenece la tarea"
    )
    asignado_a = models.ForeignKey(
        Empleados,
        on_delete=models.PROTECT,
        related_name='tareas_asignadas',
        verbose_name='Asignado a',
        help_text="Empleado asignado a la tarea"
    )
    estado = models.ForeignKey(
        Estados,
        on_delete=models.PROTECT,
        verbose_name='Estado',
        help_text="Estado actual de la tarea"
    )
    completada = models.BooleanField(
        'Completada',
        default=False,
        help_text="Indica si la tarea está completada"
    )

    class Meta:
        db_table = 'tareas'
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['proyecto', 'prioridad__nivel', 'fecha_inicio']
        indexes = [
            models.Index(fields=['proyecto', 'estado']),
            models.Index(fields=['asignado_a', 'completada']),
            models.Index(fields=['prioridad', 'fecha_fin_estimada']),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.proyecto.nombre}"

    def clean(self):
        """Validaciones personalizadas."""
        if self.fecha_fin_estimada and self.fecha_inicio:
            if self.fecha_fin_estimada <= self.fecha_inicio:
                raise ValidationError(
                    'La fecha de fin estimada debe ser posterior a la fecha de inicio.'
                )


class Subtarea(TimestampedModel):
    """
    Modelo para gestionar las subtareas de una tarea.
    """
    id_subtarea = models.AutoField(
        'ID Subtarea',
        primary_key=True
    )
    uuid = models.UUIDField(
        'UUID',
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    nombre_subtarea = models.CharField(
        'Nombre de la Subtarea',
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text="Nombre de la subtarea"
    )
    descripcion = models.TextField(
        'Descripción',
        help_text="Descripción detallada de la subtarea"
    )
    duracion_estimada = models.PositiveIntegerField(
        'Duración Estimada (horas)',
        validators=[MinValueValidator(1)],
        help_text="Duración estimada en horas"
    )
    duracion_real = models.PositiveIntegerField(
        'Duración Real (horas)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Duración real en horas"
    )
    fecha_inicio = models.DateTimeField(
        'Fecha de Inicio',
        default=timezone.now,
        help_text="Fecha y hora de inicio"
    )
    fecha_fin_estimada = models.DateTimeField(
        'Fecha de Fin Estimada',
        help_text="Fecha y hora estimada de finalización"
    )
    fecha_fin_real = models.DateTimeField(
        'Fecha de Fin Real',
        null=True,
        blank=True,
        help_text="Fecha y hora real de finalización"
    )
    tarea = models.ForeignKey(
        Tareas,
        on_delete=models.CASCADE,
        related_name='subtareas',
        verbose_name='Tarea',
        help_text="Tarea a la que pertenece la subtarea"
    )
    asignado_a = models.ForeignKey(
        Empleados,
        on_delete=models.PROTECT,
        related_name='subtareas_asignadas',
        verbose_name='Asignado a',
        help_text="Empleado asignado a la subtarea"
    )
    completada = models.BooleanField(
        'Completada',
        default=False,
        help_text="Indica si la subtarea está completada"
    )

    class Meta:
        db_table = 'subtarea'
        verbose_name = 'Subtarea'
        verbose_name_plural = 'Subtareas'
        ordering = ['tarea', 'fecha_inicio']
        indexes = [
            models.Index(fields=['tarea', 'completada']),
            models.Index(fields=['asignado_a']),
        ]

    def __str__(self):
        return f"{self.nombre_subtarea} - {self.tarea.nombre}"

    def clean(self):
        """Validaciones personalizadas."""
        if self.fecha_fin_estimada and self.fecha_inicio:
            if self.fecha_fin_estimada <= self.fecha_inicio:
                raise ValidationError(
                    'La fecha de fin estimada debe ser posterior a la fecha de inicio.'
                )


class EmpleadosProyecto(TimestampedModel):
    """
    Modelo intermedio para la relación muchos a muchos entre Empleados y Proyectos.
    """
    id_emple_vs_proye = models.UUIDField(
        'ID Empleado vs Proyecto',
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    empleado = models.ForeignKey(
        Empleados,
        on_delete=models.CASCADE,
        related_name='proyectos_asignados',
        verbose_name='Empleado'
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='empleados_asignados',
        verbose_name='Proyecto'
    )
    fecha_asignacion = models.DateTimeField(
        'Fecha de Asignación',
        default=timezone.now,
        help_text="Fecha de asignación al proyecto"
    )
    fecha_desasignacion = models.DateTimeField(
        'Fecha de Desasignación',
        null=True,
        blank=True,
        help_text="Fecha de desasignación del proyecto"
    )
    rol_en_proyecto = models.CharField(
        'Rol en el Proyecto',
        max_length=100,
        blank=True,
        null=True,
        help_text="Rol específico del empleado en este proyecto"
    )
    activo = models.BooleanField(
        'Activo',
        default=True,
        help_text="Indica si la asignación está activa"
    )

    class Meta:
        db_table = 'empleados_proyecto'
        verbose_name = 'Asignación Empleado-Proyecto'
        verbose_name_plural = 'Asignaciones Empleado-Proyecto'
        unique_together = ['empleado', 'proyecto', 'activo']
        ordering = ['-fecha_asignacion']
        indexes = [
            models.Index(fields=['empleado', 'activo']),
            models.Index(fields=['proyecto', 'activo']),
        ]

    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.proyecto.nombre}"

    def clean(self):
        """Validaciones personalizadas."""
        if self.fecha_desasignacion and self.fecha_asignacion:
            if self.fecha_desasignacion <= self.fecha_asignacion:
                raise ValidationError(
                    'La fecha de desasignación debe ser posterior a la fecha de asignación.'
                )
