# Proyecto Aurora - Sistema de Gestión de Empleados y Proyectos

## Descripción
Aurora es una API REST desarrollada con Django REST Framework para la gestión integral de empleados, proyectos, tareas y subtareas en una organización. El sistema permite administrar la información de empleados, organizar proyectos por áreas y prioridades, y realizar un seguimiento detallado de tareas y subtareas.

## Características Principales

### 📊 Gestión de Empleados
- Registro y autenticación de empleados
- Asignación por áreas y cargos
- Manejo seguro de credenciales con encriptación

### 🏢 Organización por Áreas
- Creación y gestión de áreas departamentales
- Asignación de empleados por áreas
- Control de estados por área

### 📋 Gestión de Proyectos
- Creación y seguimiento de proyectos
- Sistema de prioridades
- Control de estados del proyecto
- Estimación de duración

### ✅ Sistema de Tareas y Subtareas
- Creación de tareas asociadas a proyectos
- División en subtareas para mejor organización
- Sistema de prioridades granular
- Seguimiento de tiempos estimados vs reales

### 🔐 Seguridad y Autenticación
- Sistema de autenticación robusto
- Manejo seguro de contraseñas
- Control de permisos por endpoint
- Soporte para tokens de autenticación

### 📚 Documentación API
- Documentación interactiva con Swagger UI
- Especificación OpenAPI completa
- Interfaz ReDoc alternativa

## Tecnologías Utilizadas

- **Backend**: Django 4.2 + Django REST Framework 3.15.2
- **Base de Datos**: MySQL con soporte para PostgreSQL
- **Documentación**: drf-yasg (Swagger/OpenAPI)
- **Autenticación**: Django Auth + Token Authentication
- **CORS**: django-cors-headers
- **Variables de Entorno**: python-dotenv

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+ o PostgreSQL 12+
- pip (gestor de paquetes de Python)

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd aurora
```

### 2. Crear Entorno Virtual
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# o
env\Scripts\activate  # Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# Configuración de Django
SECRET_KEY=tu-clave-secreta-muy-segura
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.56.1

# Configuración de Base de Datos
DB_NAME=aurora
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
```

### 5. Configurar Base de Datos
```bash
# Crear la base de datos (MySQL)
mysql -u root -p
CREATE DATABASE aurora CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7. Ejecutar el Servidor
```bash
python manage.py runserver
```

## Uso de la API

### Endpoints Principales

- **Autenticación**:
  - `POST /api/login/` - Iniciar sesión
  - `POST /api/logout/` - Cerrar sesión

- **Empleados**: 
  - `GET /api/empleados/` - Listar empleados
  - `POST /api/empleados/` - Crear empleado
  - `GET /api/empleados/{id}/` - Detalle de empleado
  - `PUT /api/empleados/{id}/` - Actualizar empleado
  - `DELETE /api/empleados/{id}/` - Eliminar empleado

- **Proyectos**:
  - `GET /api/proyectos/` - Listar proyectos
  - `POST /api/proyectos/` - Crear proyecto
  - `GET /api/proyectos/{id}/` - Detalle de proyecto

- **Tareas**:
  - `GET /api/tareas/` - Listar tareas
  - `POST /api/tareas/` - Crear tarea

- **Áreas, Cargos, Estados, Prioridades**: 
  - Endpoints CRUD completos para cada entidad

### Documentación Interactiva

Una vez ejecutando el servidor, accede a:
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/

## Estructura del Proyecto

```
aurora/
├── aurora/                 # Configuración principal del proyecto
│   ├── settings.py        # Configuraciones
│   ├── urls.py           # URLs principales
│   ├── wsgi.py           # Configuración WSGI
│   └── asgi.py           # Configuración ASGI
├── app/                   # Aplicación principal
│   ├── models.py         # Modelos de datos
│   ├── views.py          # Vistas de API
│   ├── serializers.py    # Serializers de DRF
│   ├── admin.py          # Configuración admin
│   ├── tests.py          # Tests unitarios
│   └── urls.py           # URLs de la app
├── manage.py             # Comando principal Django
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## Testing

Ejecutar tests:
```bash
# Todos los tests
python manage.py test

# Tests específicos
python manage.py test app.tests.APITestCase

# Con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

- Email: soporte@tuempresa.com
- Documentación: http://localhost:8000/swagger/

## Notas de Desarrollo

### Variables de Entorno Importantes
- `DJANGO_DEBUG`: Controla el modo debug (True/False)
- `SECRET_KEY`: Clave secreta de Django (cambiar en producción)
- `DJANGO_ALLOWED_HOSTS`: Hosts permitidos separados por coma

### Consideraciones de Seguridad
- Las contraseñas se almacenan con hash seguro
- Tokens de autenticación para acceso API
- CORS configurado para desarrollo
- Variables sensibles en archivo .env (no incluir en git)

### Optimizaciones Implementadas
- Select_related en queries de proyectos
- Validaciones a nivel de modelo y serializer
- Manejo de errores personalizado
- Tests unitarios comprehensivos
