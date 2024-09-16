from django.db import models


class Area(models.Model):
    id_area = models.AutoField(db_column='ID_Area', primary_key=True)  # Field name made lowercase.
    nombre_area = models.CharField(db_column='Nombre_Area', max_length=45, blank=True, null=True)  # Field name made lowercase.
    descripcion_area = models.CharField(db_column='Descripcion_Area', max_length=45, blank=True, null=True)  # Field name made lowercase.
    estados_id_estados = models.ForeignKey('Estados', models.DO_NOTHING, db_column='estados_ID_Estados')  # Field name made lowercase.
    fecha_creada = models.DateTimeField(db_column='Fecha_Creada')  # Field name made lowercase.
    fecha_actualizacion = models.DateTimeField(db_column='Fecha_Actualizacion')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'area'


class Cargo(models.Model):
    id_cargo = models.AutoField(db_column='ID_Cargo', primary_key=True)  # Field name made lowercase.
    cargo = models.CharField(max_length=45, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cargo'


class Empleados(models.Model):
    id_empleado = models.AutoField(db_column='ID_Empleado', primary_key=True)  # Field name made lowercase. The composite primary key (ID_Empleado, area_ID_Area) found, that is not supported. The first column is selected.
    nombres = models.CharField(db_column='Nombres', max_length=45, blank=True, null=True)  # Field name made lowercase.
    apellidos = models.CharField(db_column='Apellidos', max_length=45, blank=True, null=True)  # Field name made lowercase.
    correo_electronico = models.CharField(db_column='Correo_Electronico', unique=True, max_length=45, blank=True, null=True)  # Field name made lowercase.
    contrasena = models.CharField(db_column='Contrasena', max_length=500, blank=True, null=True)  # Field name made lowercase.
    celular = models.CharField(db_column='Celular', unique=True, max_length=45, blank=True, null=True)  # Field name made lowercase.
    login = models.CharField(db_column='Login', unique=True, max_length=45, blank=True, null=True)  # Field name made lowercase.
    cargo = models.ForeignKey(Cargo, models.DO_NOTHING, db_column='Cargo_id')  # Field name made lowercase.
    estados_id_estados = models.ForeignKey('Estados', models.DO_NOTHING, db_column='estados_ID_Estados')  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')  # Field name made lowercase.
    fecha_actualizacion = models.DateTimeField(db_column='Fecha_Actualizacion')  # Field name made lowercase.
    area_id_area = models.ForeignKey(Area, models.DO_NOTHING, db_column='area_ID_Area')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'empleados'
        unique_together = (('id_empleado', 'area_id_area'),)


class EmpleadosProyecto(models.Model):
    id_emple_vs_proye = models.CharField(db_column='ID_emple_vs_proye', primary_key=True, max_length=45)  # Field name made lowercase. The composite primary key (ID_emple_vs_proye, Empleados_ID_Empleado, Proyecto_ID_Proyecto) found, that is not supported. The first column is selected.
    empleados_id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Empleados_ID_Empleado')  # Field name made lowercase.
    proyecto_id_proyecto = models.ForeignKey('Proyecto', models.DO_NOTHING, db_column='Proyecto_ID_Proyecto')  # Field name made lowercase.
    fecha_asignacion = models.DateTimeField(db_column='Fecha_asignacion')  # Field name made lowercase.
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'empleados_proyecto'
        unique_together = (('id_emple_vs_proye', 'empleados_id_empleado', 'proyecto_id_proyecto'),)


class Estados(models.Model):
    id_estados = models.AutoField(db_column='ID_Estados', primary_key=True)  # Field name made lowercase.
    nombre_estado = models.CharField(db_column='Nombre_estado', max_length=45, blank=True, null=True)  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')  # Field name made lowercase.
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'estados'


class Prioridad(models.Model):
    id_prioridad = models.AutoField(db_column='ID_Prioridad', primary_key=True)  # Field name made lowercase.
    nombre_prioridad = models.CharField(db_column='Nombre_prioridad', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
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
        managed = False
        db_table = 'proyecto'


class Subtarea(models.Model):
    id_subtarea = models.AutoField(db_column='Id_subtarea', primary_key=True)  # Field name made lowercase. The composite primary key (Id_subtarea, tareas_ID_Tareas) found, that is not supported. The first column is selected.
    nombre = models.CharField(db_column='Nombre', max_length=45, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=45, blank=True, null=True)  # Field name made lowercase.
    fecha_creacion = models.DateTimeField(db_column='Fecha_Creacion')  # Field name made lowercase.
    estados_id_estados = models.ForeignKey(Estados, models.DO_NOTHING, db_column='Estados_ID_Estados')  # Field name made lowercase.
    fecha_fin = models.DateTimeField(db_column='Fecha_Fin')  # Field name made lowercase.
    tareas_id_tareas = models.ForeignKey('Tareas', models.DO_NOTHING, db_column='tareas_ID_Tareas')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'subtarea'
        unique_together = (('id_subtarea', 'tareas_id_tareas'),)


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
        managed = False
        db_table = 'tareas'
