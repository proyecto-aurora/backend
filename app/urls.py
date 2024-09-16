from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views import (
    AreaViewSet, CargoViewSet, EmpleadosViewSet, ProyectoViewSet, 
    TareasViewSet, SubtareaViewSet, EstadosViewSet, PrioridadViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Configuración del router para las vistas API
router = DefaultRouter()
router.register(r'area', AreaViewSet)
router.register(r'cargo', CargoViewSet)
router.register(r'empleados', EmpleadosViewSet)
router.register(r'proyecto', ProyectoViewSet)
router.register(r'tareas', TareasViewSet)
router.register(r'subtarea', SubtareaViewSet)
router.register(r'estados', EstadosViewSet)
router.register(r'prioridad', PrioridadViewSet)

# Configuración de Swagger para la documentación
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentación Aurora",
        default_version='v1',
        description="Documentación de la API para la base de datos MySQL",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="soporte@tuempresa.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Configuración de URLs
urlpatterns = [
    path('api/', include(router.urls)),  # Rutas de la API
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),  
]
