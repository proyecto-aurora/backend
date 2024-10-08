from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Area(models.Model):
    id_area = models.AutoField(db_column='ID_Area', primary_key=True)  # Field name made lowercase.
    nombre_area = models.CharField(db_column='Nombre_Area', max_length=45, blank=True, null=True)  # Field name made lowercase.
    descripcion_area = models.CharField(db_column='Descripcion_Area', max_length=45, blank=True, null=True)  # Field name made lowercase.
    estados_id_estados = models.ForeignKey('Estados', models.DO_NOTHING, db_column='estados_ID_Estados')  # Añade null=True
    fecha_creada = models.DateTimeField(db_column='Fecha_Creada', default=timezone.now)  # Field name made lowercase.
    fecha_actualizacion = models.DateTimeField(db_column='Fecha_Actualizacion', auto_now=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'area'


class Cargo(models.Model):
    id_cargo = models.AutoField(db_column='ID_Cargo', primary_key=True)  # Field name made lowercase.
    cargo = models.CharField(max_length=45, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'cargo'


class EmpleadosManager(BaseUserManager):
    def create_user(self, login, contrasena=None, **extra_fields):
        if not login:
            raise ValueError('El campo login es obligatorio')
        user = self.model(login=login, **extra_fields)
        user.set_password(contrasena)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, contrasena, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(login, contrasena, **extra_fields)

class Empleados(AbstractBaseUser, PermissionsMixin):
    id_empleado = models.AutoField(db_column='ID_Empleado', primary_key=True)
    nombres = models.CharField(db_column='Nombres', max_length=45, blank=True, null=True)
    apellidos = models.CharField(db_column='Apellidos', max_length=45, blank=True, null=True)
    correo_electronico = models.CharField(db_column='Correo_Electronico', unique=True, max_length=45, blank=True, null=True)
    contrasena = models.CharField(db_column='Contrasena', max_length=500, blank=True, null=True)
    celular = models.CharField(db_column='Celular', unique=True, max_length=45, blank=True, null=True)
    login = models.CharField(db_column='Login', unique=True, max_length=45)
    cargo = models.ForeignKey(Cargo, models.DO_NOTHING, db_column='Cargo_id')
    estados_id_estados = models.ForeignKey('Estados', models.DO_NOTHING, db_column='estados_ID_Estados')
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion', default=timezone.now)
    fecha_actualizacion = models.DateTimeField(db_column='Fecha_Actualizacion', auto_now=True)
    area_id_area = models.ForeignKey(Area, models.DO_NOTHING, db_column='area_ID_Area')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = EmpleadosManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'correo_electronico']

    class Meta:
        managed = True
        db_table = 'empleados'
        unique_together = (('id_empleado', 'area_id_area'),)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class EmpleadosProyecto(models.Model):
    id_emple_vs_proye = models.CharField(db_column='ID_emple_vs_proye', primary_key=True, max_length=45)  # Field name made lowercase. The composite primary key (ID_emple_vs_proye, Empleados_ID_Empleado, Proyecto_ID_Proyecto) found, that is not supported. The first column is selected.
    empleados_id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Empleados_ID_Empleado')  # Field name made lowercase.
    proyecto_id_proyecto = models.ForeignKey('Proyecto', models.DO_NOTHING, db_column='Proyecto_ID_Proyecto')  # Field name made lowercase.
    fecha_asignacion = models.DateTimeField(db_column='Fecha_asignacion')  # Field name made lowercase.
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'empleados_proyecto'
        unique_together = (('id_emple_vs_proye', 'empleados_id_empleado', 'proyecto_id_proyecto'),)


class Estados(models.Model):
    id_estados = models.AutoField(db_column='ID_Estados', primary_key=True)  # Field name made lowercase.
    nombre_estado = models.CharField(db_column='Nombre_estado', max_length=45, blank=True, null=True)  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')  # Field name made lowercase.
    updated_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'estados'


class Prioridad(models.Model):
    id_prioridad = models.AutoField(db_column='ID_Prioridad', primary_key=True)  # Field name made lowercase.
    nombre_prioridad = models.CharField(db_column='Nombre_prioridad', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'prioridad'


class Proyecto(models.Model):
    id_proyecto = models.AutoField(db_column='ID_Proyecto', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=45, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=45, blank=True, null=True)  # Field name made lowercase.
    duracion_estimada = models.IntegerField(db_column='Duracion_estimada', blank=True, null=True)  # Field name made lowercase.
    estados_id_estados = models.ForeignKey(Estados, models.DO_NOTHING, db_column='Estados_ID_Estados')  # Field name made lowercase.
    prioridad_id_prioridad = models.ForeignKey(Prioridad, models.DO_NOTHING, db_column='Prioridad_ID_Prioridad')  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')  # Field name made lowercase.
    fecha_fin_proyecto = models.DateTimeField(db_column='Fecha_Fin_Proyecto')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'proyecto'


class Subtarea(models.Model):
    id_subtarea = models.AutoField(db_column='ID_Subtarea', primary_key=True)  # Field name made lowercase.
    nombre_subtarea = models.CharField(db_column='Nombre_Subtarea', max_length=45, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=450, blank=True, null=True)  # Field name made lowercase.
    duracion_estimada = models.IntegerField(db_column='Duracion_estimada', blank=True, null=True)  # Field name made lowercase.
    tareas_id_tareas = models.ForeignKey('Tareas', models.DO_NOTHING, db_column='Tareas_ID_Tareas')  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')  # Field name made lowercase.
    fecha_fin = models.DateTimeField(db_column='Fecha_Fin')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'subtarea'


class Tareas(models.Model):
    id_tareas = models.AutoField(db_column='ID_Tareas', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=45, blank=True, null=True)
    descripcion = models.CharField(db_column='Descripcion', max_length=450, blank=True, null=True)  # Field name made lowercase.
    duracion_estimada = models.IntegerField(db_column='Duracion_estimada', blank=True, null=True)  # Field name made lowercase.
    prioridad_id_prioridad = models.ForeignKey(Prioridad, models.DO_NOTHING, db_column='Prioridad_ID_Prioridad')  # Field name made lowercase.
    proyecto_id_proyecto = models.ForeignKey(Proyecto, models.DO_NOTHING, db_column='proyecto_ID_Proyecto')  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')  # Field name made lowercase.
    fecha_fin = models.DateTimeField(db_column='Fecha_Fin')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'tareas'
