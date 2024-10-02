from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Importa las vistas y el router de la aplicación
from app.views import (
    AreaViewSet, CargoViewSet, EmpleadosViewSet, ProyectoViewSet,
    TareasViewSet, SubtareaViewSet, EstadosViewSet, PrioridadViewSet, LoginView
)

# Configuración del router para las vistas API
router = DefaultRouter()
router.register(r'area', AreaViewSet)
router.register(r'cargo', CargoViewSet)
router.register(r'empleados', EmpleadosViewSet)
router.register(r'proyecto', ProyectoViewSet)
router.register(r'tarea', TareasViewSet)
router.register(r'subtarea', SubtareaViewSet)  # Cambiado de subtareas a subtarea
router.register(r'estados', EstadosViewSet)
router.register(r'prioridad', PrioridadViewSet)

# Configuración de Swagger para la documentación
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentación Aurora",
        default_version='v1',
        description="Documentación de la API para la gestión de empleados, proyectos y tareas",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="soporte@tuempresa.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Configuración de URLs
urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta para el admin de Django
    path('api/', include(router.urls)),  # Rutas de la API generadas por el router
    path('api/login/', LoginView.as_view(), name='empleados_login'),  # Ruta para login

    # Rutas para la documentación de Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Documentación Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # Documentación Redoc
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # Documentación Swagger en formato JSON
]
