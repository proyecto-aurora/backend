from django.contrib.auth.hashers import make_password, check_password
from rest_framework import serializers
from .models import Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, Estados, Prioridad

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)
    contrasena = serializers.CharField(required=True)

    def validate(self, data):
        user = Empleados.objects.filter(login=data['login']).first()
        if user and check_password(data['contrasena'], user.contrasena):
            return user
        raise serializers.ValidationError("Login o contraseña incorrecta")


class LogoutSerializer(serializers.Serializer):
    # No necesitamos campos para el logout, pero podemos añadir un mensaje si lo deseamos
    message = serializers.CharField(read_only=True, default="Sesión cerrada exitosamente")


class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = '__all__'

class EmpleadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleados
        fields = ['id_empleado', 'nombres', 'apellidos', 'correo_electronico', 'celular', 'login', 'cargo', 'estados_id_estados', 'fecha_creacion', 'fecha_actualizacion', 'area_id_area', 'contrasena']
        extra_kwargs = {'contrasena': {'write_only': True}}

    def create(self, validated_data):
        validated_data['contrasena'] = make_password(validated_data.get('contrasena'))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'contrasena' in validated_data:
            validated_data['contrasena'] = make_password(validated_data.get('contrasena'))
        return super().update(instance, validated_data)

class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = '__all__'

class TareasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tareas
        fields = '__all__'

class SubtareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtarea
        fields = '__all__'

class EstadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = '__all__'

class PrioridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prioridad
        fields = '__all__'


