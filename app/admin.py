from django.contrib import admin
from .models import Area, Cargo, Empleados, EmpleadosProyecto, Estados, Prioridad, Proyecto, Subtarea, Tareas

# Registrar los modelos en el admin
admin.site.register(Area)
admin.site.register(Cargo)
admin.site.register(Empleados)
admin.site.register(EmpleadosProyecto)
admin.site.register(Estados)
admin.site.register(Prioridad)
admin.site.register(Proyecto)
admin.site.register(Subtarea)
admin.site.register(Tareas)
