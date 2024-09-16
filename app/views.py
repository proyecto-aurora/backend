from django.shortcuts import render

from rest_framework import viewsets
from .models import Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, Estados, Prioridad
from .serializers import AreaSerializer, CargoSerializer, EmpleadosSerializer, ProyectoSerializer, TareasSerializer, SubtareaSerializer, EstadosSerializer, PrioridadSerializer

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class CargoViewSet(viewsets.ModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer

class EmpleadosViewSet(viewsets.ModelViewSet):
    queryset = Empleados.objects.all()
    serializer_class = EmpleadosSerializer

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