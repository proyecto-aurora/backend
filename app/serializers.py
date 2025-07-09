"""
Serializers para la API REST del sistema Aurora.

Este módulo contiene todos los serializers para transformar los modelos
en representaciones JSON y manejar la validación de datos.

Utiliza Django REST Framework serializers para proporcionar:
- Validaciones robustas
- Transformaciones de datos
- Campos calculados y anidados
- Manejo seguro de contraseñas

Autor: Equipo de Desarrollo Aurora
Fecha: 2024
"""

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import (
    Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, 
    Estados, Prioridad, EmpleadosProyecto
)


class TimestampedSerializer(serializers.ModelSerializer):
    """
    Serializer base que incluye campos de timestamp en formato legible.
    """
    fecha_creacion_formatted = serializers.SerializerMethodField()
    fecha_actualizacion_formatted = serializers.SerializerMethodField()

    def get_fecha_creacion_formatted(self, obj):
        """Formatear fecha de creación."""
        if hasattr(obj, 'fecha_creacion') and obj.fecha_creacion:
            return obj.fecha_creacion.strftime('%d/%m/%Y %H:%M')
        return None

    def get_fecha_actualizacion_formatted(self, obj):
        """Formatear fecha de actualización."""
        if hasattr(obj, 'fecha_actualizacion') and obj.fecha_actualizacion:
            return obj.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')
        return None


class EstadosSerializer(TimestampedSerializer):
    """
    Serializer para el modelo Estados.
    """
    class Meta:
        model = Estados
        fields = [
            'id_estados', 'nombre_estado', 'descripcion', 'activo',
            'fecha_creacion', 'fecha_actualizacion',
            'fecha_creacion_formatted', 'fecha_actualizacion_formatted'
        ]
        read_only_fields = ['id_estados', 'fecha_creacion', 'fecha_actualizacion']

    def validate_nombre_estado(self, value):
        """Validar nombre del estado."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El nombre del estado debe tener al menos 2 caracteres."
            )
        return value.strip().title()


class PrioridadSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Prioridad.
    """
    class Meta:
        model = Prioridad
        fields = ['id_prioridad', 'nombre_prioridad', 'nivel', 'color', 'activo']
        read_only_fields = ['id_prioridad']

    def validate_nivel(self, value):
        """Validar que el nivel sea único."""
        if self.instance:
            # Excluir la instancia actual en la validación de actualización
            if Prioridad.objects.filter(nivel=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    "Ya existe una prioridad con este nivel."
                )
        elif Prioridad.objects.filter(nivel=value).exists():
            raise serializers.ValidationError(
                "Ya existe una prioridad con este nivel."
            )
        return value

    def validate_color(self, value):
        """Validar formato de color hexadecimal."""
        import re
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
            raise serializers.ValidationError(
                "El color debe estar en formato hexadecimal (#RRGGBB o #RGB)."
            )
        return value


class CargoSerializer(TimestampedSerializer):
    """
    Serializer para el modelo Cargo.
    """
    empleados_count = serializers.SerializerMethodField()

    class Meta:
        model = Cargo
        fields = [
            'id_cargo', 'nombre_cargo', 'descripcion', 'nivel_jerarquico',
            'salario_base', 'activo', 'empleados_count',
            'fecha_creacion', 'fecha_actualizacion',
            'fecha_creacion_formatted', 'fecha_actualizacion_formatted'
        ]
        read_only_fields = ['id_cargo', 'fecha_creacion', 'fecha_actualizacion']

    def get_empleados_count(self, obj):
        """Obtener cantidad de empleados con este cargo."""
        return obj.empleados_set.filter(is_active=True).count()

    def validate_salario_base(self, value):
        """Validar salario base."""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "El salario base no puede ser negativo."
            )
        return value

    def validate_nivel_jerarquico(self, value):
        """Validar nivel jerárquico."""
        if value < 1:
            raise serializers.ValidationError(
                "El nivel jerárquico debe ser mayor a 0."
            )
        return value


class AreaSerializer(TimestampedSerializer):
    """
    Serializer para el modelo Area.
    """
    estado = EstadosSerializer(read_only=True)
    estado_id = serializers.IntegerField(write_only=True, source='estado.id_estados')
    responsable = serializers.StringRelatedMethod(read_only=True)
    responsable_id = serializers.IntegerField(
        write_only=True, 
        source='responsable.id_empleado',
        required=False,
        allow_null=True
    )
    empleados_count = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = [
            'id_area', 'nombre_area', 'descripcion_area', 
            'estado', 'estado_id', 'responsable', 'responsable_id',
            'empleados_count',
            'fecha_creacion', 'fecha_actualizacion',
            'fecha_creacion_formatted', 'fecha_actualizacion_formatted'
        ]
        read_only_fields = ['id_area', 'fecha_creacion', 'fecha_actualizacion']

    def get_empleados_count(self, obj):
        """Obtener cantidad de empleados en el área."""
        return obj.empleados.filter(is_active=True).count()

    def validate_estado_id(self, value):
        """Validar que el estado exista."""
        try:
            Estados.objects.get(id_estados=value, activo=True)
        except Estados.DoesNotExist:
            raise serializers.ValidationError(
                "El estado especificado no existe o está inactivo."
            )
        return value

    def validate_responsable_id(self, value):
        """Validar que el responsable exista y esté activo."""
        if value:
            try:
                empleado = Empleados.objects.get(id_empleado=value, is_active=True)
                # Validar que el empleado esté en la misma área (solo para actualización)
                if self.instance and empleado.area != self.instance:
                    raise serializers.ValidationError(
                        "El responsable debe pertenecer al área que va a liderar."
                    )
            except Empleados.DoesNotExist:
                raise serializers.ValidationError(
                    "El empleado especificado no existe o está inactivo."
                )
        return value


class EmpleadosSerializer(TimestampedSerializer):
    """
    Serializer para el modelo Empleados (Usuario personalizado).
    """
    # Campos de lectura anidados
    cargo = CargoSerializer(read_only=True)
    estado = EstadosSerializer(read_only=True)
    area = AreaSerializer(read_only=True)
    
    # Campos de escritura
    cargo_id = serializers.IntegerField(write_only=True, source='cargo.id_cargo')
    estado_id = serializers.IntegerField(write_only=True, source='estado.id_estados')
    area_id = serializers.IntegerField(write_only=True, source='area.id_area')
    
    # Campos calculados
    nombre_completo = serializers.ReadOnlyField()
    edad = serializers.ReadOnlyField()
    
    # Campo de contraseña seguro
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        help_text="Mínimo 8 caracteres. Debe incluir letras y números."
    )
    
    # Validadores para campos únicos
    correo_electronico = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Empleados.objects.all(),
                message="Ya existe un empleado con este correo electrónico."
            )
        ]
    )
    celular = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Empleados.objects.all(),
                message="Ya existe un empleado con este número de celular."
            )
        ]
    )
    login = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Empleados.objects.all(),
                message="Ya existe un empleado con este nombre de usuario."
            )
        ]
    )

    class Meta:
        model = Empleados
        fields = [
            'id_empleado', 'uuid', 'nombres', 'apellidos', 'nombre_completo',
            'correo_electronico', 'celular', 'login', 'edad',
            'cargo', 'cargo_id', 'estado', 'estado_id', 'area', 'area_id',
            'fecha_ingreso', 'fecha_nacimiento', 'is_active', 'is_staff',
            'password',
            'fecha_creacion', 'fecha_actualizacion',
            'fecha_creacion_formatted', 'fecha_actualizacion_formatted'
        ]
        read_only_fields = [
            'id_empleado', 'uuid', 'fecha_creacion', 'fecha_actualizacion',
            'nombre_completo', 'edad'
        ]

    def validate_password(self, value):
        """Validar fortaleza de la contraseña."""
        import re
        
        if len(value) < 8:
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres."
            )
        
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos una letra."
            )
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos un número."
            )
        
        return value

    def validate_fecha_nacimiento(self, value):
        """Validar fecha de nacimiento."""
        if value and value >= timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de nacimiento debe ser anterior a la fecha actual."
            )
        
        # Validar edad mínima (18 años)
        if value:
            today = timezone.now().date()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 18:
                raise serializers.ValidationError(
                    "El empleado debe ser mayor de 18 años."
                )
        
        return value

    def validate_fecha_ingreso(self, value):
        """Validar fecha de ingreso."""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de ingreso no puede ser futura."
            )
        return value

    def create(self, validated_data):
        """Crear empleado con contraseña encriptada."""
        password = validated_data.pop('password')
        empleado = Empleados.objects.create_user(
            login=validated_data['login'],
            contrasena=password,
            **validated_data
        )
        return empleado

    def update(self, instance, validated_data):
        """Actualizar empleado manejando contraseña."""
        password = validated_data.pop('password', None)
        
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ProyectoSerializer(TimestampedSerializer):
    """
    Serializer para el modelo Proyecto.
    """
    # Campos anidados de lectura
    estado = EstadosSerializer(read_only=True)
    prioridad = PrioridadSerializer(read_only=True)
    responsable = EmpleadosSerializer(read_only=True, fields=['id_empleado', 'nombre_completo', 'cargo'])
    
    # Campos de escritura
    estado_id = serializers.IntegerField(write_only=True, source='estado.id_estados')
    prioridad_id = serializers.IntegerField(write_only=True, source='prioridad.id_prioridad')
    responsable_id = serializers.IntegerField(write_only=True, source='responsable.id_empleado')
    
    # Campos calculados
    progreso_temporal = serializers.ReadOnlyField()
    dias_restantes = serializers.SerializerMethodField()
    tareas_count = serializers.SerializerMethodField()

    class Meta:
        model = Proyecto
        fields = [
            'id_proyecto', 'uuid', 'nombre', 'descripcion', 'duracion_estimada',
            'fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real',
            'estado', 'estado_id', 'prioridad', 'prioridad_id',
            'responsable', 'responsable_id', 'presupuesto',
            'progreso_temporal', 'dias_restantes', 'tareas_count',
            'fecha_creacion', 'fecha_actualizacion',
            'fecha_creacion_formatted', 'fecha_actualizacion_formatted'
        ]
        read_only_fields = [
            'id_proyecto', 'uuid', 'fecha_creacion', 'fecha_actualizacion',
            'progreso_temporal'
        ]

    def get_dias_restantes(self, obj):
        """Calcular días restantes del proyecto."""
        if obj.fecha_fin_estimada:
            today = timezone.now().date()
            delta = obj.fecha_fin_estimada - today
            return delta.days if delta.days > 0 else 0
        return None

    def get_tareas_count(self, obj):
        """Obtener cantidad de tareas del proyecto."""
        return obj.tareas.count()

    def validate(self, data):
        """Validaciones cruzadas."""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin_estimada = data.get('fecha_fin_estimada')
        
        if fecha_inicio and fecha_fin_estimada:
            if fecha_fin_estimada <= fecha_inicio:
                raise serializers.ValidationError(
                    "La fecha de fin estimada debe ser posterior a la fecha de inicio."
                )
        
        return data

    def validate_duracion_estimada(self, value):
        """Validar duración estimada."""
        if value <= 0:
            raise serializers.ValidationError(
                "La duración estimada debe ser mayor a 0 días."
            )
        return value

    def validate_presupuesto(self, value):
        """Validar presupuesto."""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "El presupuesto no puede ser negativo."
            )
        return value


class TareasSerializer(TimestampedSerializer):
    """
    Serializer para el modelo Tareas.
    """
    # Campos anidados
    proyecto = ProyectoSerializer(read_only=True, fields=['id_proyecto', 'nombre'])
    prioridad = PrioridadSerializer(read_only=True)
    asignado_a = EmpleadosSerializer(read_only=True, fields=['id_empleado', 'nombre_completo'])
    estado = EstadosSerializer(read_only=True)
    
    # Campos de escritura
    proyecto_id = serializers.IntegerField(write_only=True, source='proyecto.id_proyecto')
    prioridad_id = serializers.IntegerField(write_only=True, source='prioridad.id_prioridad')
    asignado_a_id = serializers.IntegerField(write_only=True, source='asignado_a.id_empleado')
    estado_id = serializers.IntegerField(write_only=True, source='estado.id_estados')
    
    # Campos calculados
    tiempo_transcurrido = serializers.SerializerMethodField()
    subtareas_count = serializers.SerializerMethodField()

    class Meta:
        model = Tareas
        fields = [
            'id_tareas', 'uuid', 'nombre', 'descripcion', 
            'duracion_estimada', 'duracion_real', 'fecha_inicio', 
            'fecha_fin_estimada', 'fecha_fin_real', 'completada',
            'proyecto', 'proyecto_id', 'prioridad', 'prioridad_id',
            'asignado_a', 'asignado_a_id', 'estado', 'estado_id',
            'tiempo_transcurrido', 'subtareas_count',
            'fecha_creacion', 'fecha_actualizacion',
            'fecha_creacion_formatted', 'fecha_actualizacion_formatted'
        ]
        read_only_fields = [
            'id_tareas', 'uuid', 'fecha_creacion', 'fecha_actualizacion'
        ]

    def get_tiempo_transcurrido(self, obj):
        """Calcular tiempo transcurrido desde el inicio."""
        if obj.fecha_inicio:
            now = timezone.now()
            delta = now - obj.fecha_inicio
            return delta.total_seconds() / 3600  # En horas
        return 0

    def get_subtareas_count(self, obj):
        """Obtener cantidad de subtareas."""
        return obj.subtareas.count()

    def validate(self, data):
        """Validaciones cruzadas."""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin_estimada = data.get('fecha_fin_estimada')
        
        if fecha_inicio and fecha_fin_estimada:
            if fecha_fin_estimada <= fecha_inicio:
                raise serializers.ValidationError(
                    "La fecha de fin estimada debe ser posterior a la fecha de inicio."
                )
        
        return data


class SubtareaSerializer(TimestampedSerializer):
    """
    Serializer para el modelo Subtarea.
    """
    # Campos anidados
    tarea = TareasSerializer(read_only=True, fields=['id_tareas', 'nombre'])
    asignado_a = EmpleadosSerializer(read_only=True, fields=['id_empleado', 'nombre_completo'])
    
    # Campos de escritura
    tarea_id = serializers.IntegerField(write_only=True, source='tarea.id_tareas')
    asignado_a_id = serializers.IntegerField(write_only=True, source='asignado_a.id_empleado')

    class Meta:
        model = Subtarea
        fields = [
            'id_subtarea', 'uuid', 'nombre_subtarea', 'descripcion',
            'duracion_estimada', 'duracion_real', 'fecha_inicio',
            'fecha_fin_estimada', 'fecha_fin_real', 'completada',
            'tarea', 'tarea_id', 'asignado_a', 'asignado_a_id',
            'fecha_creacion', 'fecha_actualizacion',
            'fecha_creacion_formatted', 'fecha_actualizacion_formatted'
        ]
        read_only_fields = [
            'id_subtarea', 'uuid', 'fecha_creacion', 'fecha_actualizacion'
        ]

    def validate(self, data):
        """Validaciones cruzadas."""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin_estimada = data.get('fecha_fin_estimada')
        
        if fecha_inicio and fecha_fin_estimada:
            if fecha_fin_estimada <= fecha_inicio:
                raise serializers.ValidationError(
                    "La fecha de fin estimada debe ser posterior a la fecha de inicio."
                )
        
        return data


class EmpleadosProyectoSerializer(TimestampedSerializer):
    """
    Serializer para el modelo EmpleadosProyecto.
    """
    empleado = EmpleadosSerializer(read_only=True, fields=['id_empleado', 'nombre_completo', 'cargo'])
    proyecto = ProyectoSerializer(read_only=True, fields=['id_proyecto', 'nombre'])
    
    empleado_id = serializers.IntegerField(write_only=True, source='empleado.id_empleado')
    proyecto_id = serializers.IntegerField(write_only=True, source='proyecto.id_proyecto')

    class Meta:
        model = EmpleadosProyecto
        fields = [
            'id_emple_vs_proye', 'empleado', 'empleado_id', 'proyecto', 'proyecto_id',
            'fecha_asignacion', 'fecha_desasignacion', 'rol_en_proyecto', 'activo',
            'fecha_creacion', 'fecha_actualizacion',
            'fecha_creacion_formatted', 'fecha_actualizacion_formatted'
        ]
        read_only_fields = ['id_emple_vs_proye', 'fecha_creacion', 'fecha_actualizacion']

    def validate(self, data):
        """Validar que no exista asignación activa duplicada."""
        empleado = data.get('empleado')
        proyecto = data.get('proyecto')
        activo = data.get('activo', True)
        
        if activo and empleado and proyecto:
            # Verificar duplicación solo para asignaciones activas
            existing = EmpleadosProyecto.objects.filter(
                empleado=empleado,
                proyecto=proyecto,
                activo=True
            )
            
            # Excluir la instancia actual en caso de actualización
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "El empleado ya está asignado activamente a este proyecto."
                )
        
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer para la autenticación de empleados.
    """
    login = serializers.CharField(
        max_length=50,
        help_text="Nombre de usuario del empleado"
    )
    contrasena = serializers.CharField(
        max_length=128,
        style={'input_type': 'password'},
        help_text="Contraseña del empleado"
    )

    def validate(self, data):
        """Validar credenciales."""
        login = data.get('login')
        contrasena = data.get('contrasena')

        if not login or not contrasena:
            raise serializers.ValidationError(
                "Debe proporcionar tanto el login como la contraseña."
            )

        # Verificar que el usuario existe y está activo
        try:
            empleado = Empleados.objects.get(login=login, is_active=True)
        except Empleados.DoesNotExist:
            raise serializers.ValidationError(
                "Credenciales inválidas o usuario inactivo."
            )

        # Verificar contraseña
        if not check_password(contrasena, empleado.password):
            raise serializers.ValidationError(
                "Credenciales inválidas."
            )

        data['empleado'] = empleado
        return data


class LogoutSerializer(serializers.Serializer):
    """
    Serializer para el logout de empleados.
    """
    message = serializers.CharField(
        read_only=True, 
        default="Sesión cerrada exitosamente",
        help_text="Mensaje de confirmación de logout"
    )


