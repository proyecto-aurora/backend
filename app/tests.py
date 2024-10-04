from django.test import TestCase
from django.core.management import call_command
from django.db import connection
from django.conf import settings
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import Area, Cargo, Empleados, Proyecto, Tareas, Subtarea, Estados, Prioridad

class APITestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Asegúrate de que la base de datos de prueba esté creada y las tablas estén sincronizadas
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DATABASES['default']['TEST']['NAME']}")
        call_command('migrate', '--run-syncdb', verbosity=0)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # No eliminamos la base de datos de prueba aquí

    @classmethod
    def setUpTestData(cls):
        # Crear datos que no cambiarán entre tests
        cls.estado = Estados.objects.create(
            nombre_estado="Activo",
            fecha_creacion=timezone.now(),
            updated_at=timezone.now()
        )
        cls.area = Area.objects.create(
            nombre_area="IT", 
            descripcion_area="Tecnología", 
            estados_id_estados=cls.estado,
            fecha_creada=timezone.now(),
            fecha_actualizacion=timezone.now()
        )
        cls.cargo = Cargo.objects.create(
            cargo="Desarrollador",
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        cls.prioridad = Prioridad.objects.create(nombre_prioridad="Alta")

    def setUp(self):
        # Crear datos que pueden cambiar entre tests
        self.empleado = Empleados.objects.create_user(
            login="juanperez",
            contrasena="password123",
            nombres="Juan",
            apellidos="Pérez",
            correo_electronico="juan@example.com",
            celular="1234567890",
            cargo=self.cargo,
            estados_id_estados=self.estado,
            area_id_area=self.area
        )
        self.proyecto = Proyecto.objects.create(
            nombre="Proyecto Test",
            descripcion="Descripción del proyecto",
            duracion_estimada=30,
            estados_id_estados=self.estado,
            prioridad_id_prioridad=self.prioridad,
            fecha_creacion=timezone.now(),
            fecha_fin_proyecto=timezone.now() + timezone.timedelta(days=30)
        )
        self.tarea = Tareas.objects.create(
            nombre="Tarea Test",
            descripcion="Descripción de la tarea",
            duracion_estimada=5,
            prioridad_id_prioridad=self.prioridad,
            proyecto_id_proyecto=self.proyecto,
            fecha_creacion=timezone.now(),
            fecha_fin=timezone.now() + timezone.timedelta(days=5)
        )
        self.subtarea = Subtarea.objects.create(
            nombre_subtarea="Subtarea Test",
            descripcion="Descripción de la subtarea",
            duracion_estimada=2,
            tareas_id_tareas=self.tarea,
            fecha_creacion=timezone.now(),
            fecha_fin=timezone.now() + timezone.timedelta(days=2)
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.empleado)

    def test_area_list(self):
        response = self.client.get(reverse('v1:area-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_cargo_list(self):
        response = self.client.get(reverse('v1:cargo-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_empleados_list(self):
        response = self.client.get(reverse('v1:empleados-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_proyecto_list(self):
        response = self.client.get(reverse('v1:proyecto-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_tareas_list(self):
        response = self.client.get(reverse('v1:tareas-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_subtarea_list(self):
        response = self.client.get(reverse('v1:subtarea-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_estados_list(self):
        response = self.client.get(reverse('v1:estados-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_prioridad_list(self):
        response = self.client.get(reverse('v1:prioridad-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_create_area(self):
        data = {
            "nombre_area": "Nueva Área",
            "descripcion_area": "Descripción de la nueva área",
            "estados_id_estados": self.estado.id_estados
        }
        response = self.client.post(reverse('v1:area-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_empleado(self):
        data = {
            "nombres": "María",
            "apellidos": "González",
            "correo_electronico": "maria@example.com",
            "contrasena": "password123",
            "celular": "9876543210",
            "login": "mariagonzalez",
            "cargo": self.cargo.id_cargo,
            "estados_id_estados": self.estado.id_estados,
            "area_id_area": self.area.id_area,
            # Asegúrate de incluir todos los campos requeridos aquí
        }
        response = self.client.post(reverse('v1:empleados-list'), data)
        if response.status_code != status.HTTP_201_CREATED:
            print(response.content)  # Imprime el contenido de la respuesta para depuración
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_proyecto(self):
        data = {
            "nombre": "Proyecto Actualizado",
            "descripcion": "Nueva descripción del proyecto",
            "duracion_estimada": 45,
            "estados_id_estados": self.estado.id_estados,
            "prioridad_id_prioridad": self.prioridad.id_prioridad,
            "fecha_creacion": self.proyecto.fecha_creacion.isoformat(),
            "fecha_fin_proyecto": (self.proyecto.fecha_creacion + timezone.timedelta(days=45)).isoformat()
        }
        response = self.client.put(reverse('v1:proyecto-detail', kwargs={'pk': self.proyecto.id_proyecto}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], "Proyecto Actualizado")

    def test_delete_tarea(self):
        # Eliminar primero las subtareas asociadas
        Subtarea.objects.filter(tareas_id_tareas=self.tarea).delete()
        
        response = self.client.delete(reverse('v1:tareas-detail', kwargs={'pk': self.tarea.id_tareas}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tareas.objects.filter(id_tareas=self.tarea.id_tareas).exists())

    def test_login(self):
        self.client.logout()  # Asegurarse de que no hay usuario autenticado
        data = {
            "login": "juanperez",
            "contrasena": "password123"
        }
        response = self.client.post(reverse('empleados_login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Login exitoso')

    def test_logout(self):
        response = self.client.post(reverse('empleados_logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)