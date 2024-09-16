from rest_framework import serializers
from .models import Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, Estados, Prioridad

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = '__all__'

class EmpleadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleados
        fields = '__all__'

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


